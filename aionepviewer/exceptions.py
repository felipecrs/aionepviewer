"""Exceptions for the aionepviewer library."""

from __future__ import annotations


class NepError(Exception):
    """Base exception for aionepviewer."""


class NepAuthError(NepError):
    """Raised when authentication fails or the token is invalid/expired."""


class NepConnectionError(NepError):
    """Raised when a network connection error occurs."""


class NepApiError(NepError):
    """Raised when the API returns a non-success response code."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"API error {code}: {message}")
        self.code = code
        self.message = message


class NepTimeoutError(NepConnectionError):
    """Raised when a request times out."""