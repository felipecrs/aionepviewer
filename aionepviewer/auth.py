"""Authentication layer for the NEP API."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

import aiohttp

from .const import API_BASE_PATH, DEFAULT_HEADERS, DEFAULT_HOST, TOKEN_EXPIRY_MARGIN
from .exceptions import (
    NepApiError,
    NepAuthError,
    NepConnectionError,
    NepTimeoutError,
)
from .models import AuthData, TokenInfo


class NepAuth:
    """Handles authentication and signed requests to the NEP API.

    This class manages the JWT token lifecycle and provides the low-level
    ``request`` method used by :class:`~aionepviewer.client.NepViewer`.

    Parameters
    ----------
    session:
        An ``aiohttp.ClientSession`` instance.  The caller owns the session
        and is responsible for closing it.
    email:
        NEP account email address.
    password:
        NEP account password.
    host:
        Base URL for the API (default: ``https://api.nepviewer.net``).
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        email: str,
        password: str,
        host: str = DEFAULT_HOST,
    ) -> None:
        self._session = session
        self._email = email
        self._password = password
        self._host = host.rstrip("/")
        self._token_info: TokenInfo | None = None

    @property
    def token(self) -> str | None:
        """The current JWT token, or ``None`` if not authenticated."""
        if self._token_info is None:
            return None
        return self._token_info.token

    @property
    def is_token_valid(self) -> bool:
        """Return ``True`` if the token exists and has not expired."""
        if self._token_info is None:
            return False
        return time.time() < (self._token_info.expires_at - TOKEN_EXPIRY_MARGIN)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def sign_in(self) -> AuthData:
        """Authenticate with the NEP API and store the token.

        Raises
        ------
        NepAuthError
            If the credentials are rejected.
        """
        body = {"account": self._email, "password": self._password}
        data = await self._raw_request("POST", "/sign-in", json_body=body, auth=False)
        auth_data = AuthData.from_dict(data)
        self._token_info = auth_data.token_info
        return auth_data

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated API request, refreshing the token if needed.

        Returns the ``data`` field from the API response envelope.
        """
        if not self.is_token_valid:
            await self.sign_in()
        return await self._raw_request(method, path, json_body=json_body, auth=True)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_sign(body_bytes: bytes) -> str:
        """Compute the ``sign`` header value: MD5 of the raw request body."""
        return hashlib.md5(body_bytes).hexdigest().upper()

    async def _raw_request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:
        url = f"{self._host}{API_BASE_PATH}{path}"

        body_bytes = json.dumps(json_body, separators=(",", ":")).encode() if json_body else b""

        headers = dict(DEFAULT_HEADERS)
        headers["sign"] = self._compute_sign(body_bytes)
        if auth and self._token_info is not None:
            headers["authorization"] = self._token_info.token
        else:
            headers["authorization"] = ""

        try:
            resp = await self._session.request(
                method,
                url,
                data=body_bytes if body_bytes else None,
                headers=headers,
            )
        except aiohttp.ClientError as err:
            raise NepConnectionError(f"Connection error: {err}") from err
        except TimeoutError as err:
            raise NepTimeoutError(f"Request timed out: {err}") from err

        # Handle HTTP-level 401/403 (e.g. session invalidated by another
        # device logging in with the same account — the server returns
        # HTTP 401 with an empty body).
        if resp.status in (401, 403):
            self._token_info = None
            raise NepAuthError(
                f"Authentication failed (HTTP {resp.status})"
            )

        try:
            result = await resp.json(content_type=None)
        except Exception as err:
            text = await resp.text()
            raise NepApiError(resp.status, f"Invalid JSON response: {text}") from err

        code = result.get("code", 0)
        msg = result.get("msg", "")

        if code == 401 or code == 403:
            self._token_info = None
            raise NepAuthError(f"Authentication failed: {msg}")

        if code != 200:
            raise NepApiError(code, msg)

        data: dict[str, Any] = result.get("data", {})
        return data