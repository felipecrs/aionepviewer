"""Tests for the NepViewer client."""

from __future__ import annotations

import hashlib
import json

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from aionep import NepViewer
from aionep.const import API_BASE_PATH, DEFAULT_HOST
from aionep.exceptions import NepApiError, NepAuthError

from .conftest import (
    DEVICE_LIST_RESPONSE,
    MODULES_RESPONSE,
    SIGN_IN_RESPONSE,
    SITE_LIST_RESPONSE,
    SITE_OVERVIEW_RESPONSE,
)

BASE = f"{DEFAULT_HOST}{API_BASE_PATH}"


def _mock_sign_in(m: aioresponses) -> None:
    m.post(f"{BASE}/sign-in", payload=SIGN_IN_RESPONSE)


@pytest.mark.asyncio
async def test_authenticate() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            auth = await client.authenticate()

        assert auth.user_info.email == "test@example.com"
        assert auth.token_info.token == "fake.jwt.token"
        assert auth.site_count == 1


@pytest.mark.asyncio
async def test_get_devices() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/device/list", payload=DEVICE_LIST_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            devices = await client.get_devices()

        assert len(devices) == 1
        assert devices[0].sn == "AABB1122"
        assert devices[0].now == 1500
        assert devices[0].is_online is True


@pytest.mark.asyncio
async def test_get_sites() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/site/listWithSN", payload=SITE_LIST_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            sites = await client.get_sites()

        assert len(sites) == 1
        assert sites[0].sid == "US_TEST_SITE"
        assert sites[0].site_name == "Test Site"
        assert len(sites[0].devices) == 1


@pytest.mark.asyncio
async def test_get_site_overview() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/site/overview", payload=SITE_OVERVIEW_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            overview = await client.get_site_overview("US_TEST_SITE")

        assert overview.production.today == "5.5"
        assert overview.energy.pv_panel.power == 1500
        assert overview.alert.is_ok is True
        assert overview.is_online is True
        assert len(overview.device_list) == 1


@pytest.mark.asyncio
async def test_get_site_modules() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/site/modules", payload=MODULES_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            modules_data = await client.get_site_modules("US_TEST_SITE")

        assert modules_data.total_plc == 1
        assert len(modules_data.devices) == 1
        assert modules_data.devices[0].sn == "AABB1122"
        assert len(modules_data.devices[0].modules) == 1
        assert modules_data.devices[0].modules[0].now == 400


@pytest.mark.asyncio
async def test_auth_error() -> None:
    with aioresponses() as m:
        m.post(
            f"{BASE}/sign-in",
            payload={"code": 401, "msg": "Invalid credentials", "data": {}},
        )

        async with ClientSession() as session:
            client = NepViewer(session, "bad@example.com", "wrong")
            with pytest.raises(NepAuthError):
                await client.authenticate()


@pytest.mark.asyncio
async def test_api_error() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(
            f"{BASE}/device/list",
            payload={"code": 500, "msg": "Internal Server Error", "data": {}},
        )

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            with pytest.raises(NepApiError) as exc_info:
                await client.get_devices()
            assert exc_info.value.code == 500


def test_sign_header_computed() -> None:
    """Verify that the sign header is MD5(body).upper()."""
    from aionep.auth import NepAuth

    # Empty body → well-known MD5 of empty string
    assert NepAuth._compute_sign(b"") == "D41D8CD98F00B204E9800998ECF8427E"

    # Known body
    body = b'{"sid":"BR_20260317_tXFI"}'
    expected = hashlib.md5(body).hexdigest().upper()
    assert NepAuth._compute_sign(body) == expected

    # Compact JSON (no spaces)
    body2 = json.dumps({"sid": "TEST"}, separators=(",", ":")).encode()
    expected2 = hashlib.md5(body2).hexdigest().upper()
    assert NepAuth._compute_sign(body2) == expected2