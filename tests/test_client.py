"""Tests for the NepViewer client."""

from __future__ import annotations

import hashlib
import json

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from aionepviewer import NepViewer
from aionepviewer.const import API_BASE_PATH, DEFAULT_HOST
from aionepviewer.exceptions import NepApiError, NepAuthError

from .conftest import (
    ACCOUNT_INFO_RESPONSE,
    DEVICE_LIST_RESPONSE,
    DEVICE_WIFI_OTA_RESPONSE,
    LOGOUT_RESPONSE,
    MODULES_RESPONSE,
    PRODUCT_INFO_RESPONSE,
    REPORT_SETTINGS_RESPONSE,
    REPORT_SETUP_RESPONSE,
    SIGN_IN_RESPONSE,
    SITE_LAYOUT_RESPONSE,
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


@pytest.mark.asyncio
async def test_get_product_info() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/product/sn/info", payload=PRODUCT_INFO_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            products = await client.get_product_info(["86D4EC90"])

        assert len(products) == 1
        assert products[0].sn == "86D4EC90"
        assert products[0].model_name == "BDM-2250"
        assert len(products[0].functions) == 3
        assert products[0].functions[0].signal_ap is True


@pytest.mark.asyncio
async def test_get_device_wifi_ota() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/device/detailWifiOta", payload=DEVICE_WIFI_OTA_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            results = await client.get_device_wifi_ota([("86d33ec0", "")])

        assert len(results) == 1
        assert results[0].sn == "86d33ec0"
        assert results[0].wifi_version == "3.01.25"
        assert results[0].update_available is False


@pytest.mark.asyncio
async def test_get_site_layout() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/site/layoutInfo", payload=SITE_LAYOUT_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            layout = await client.get_site_layout("BR_20260317_tXFI")

        assert layout.sid == "BR_20260317_tXFI"
        assert layout.site_name == "Test Site"


@pytest.mark.asyncio
async def test_get_account_info() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/account/info", payload=ACCOUNT_INFO_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            info = await client.get_account_info()

        assert info.uid == "20260317190316_sQux"
        assert info.email == "test@example.com"
        assert info.country_code == "BR"
        assert info.contact_person == "Test User"
        assert info.group_name == "End User - Layout"


@pytest.mark.asyncio
async def test_logout() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/account/loginOut", payload=LOGOUT_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            await client.authenticate()
            assert client._auth.token is not None  # noqa: SLF001
            await client.logout()
            assert client._auth.token is None  # noqa: SLF001


@pytest.mark.asyncio
async def test_get_report_settings() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/site/sn/report/settings", payload=REPORT_SETTINGS_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            settings = await client.get_report_settings("BR_TEST", "86D4EC90")

        assert settings.sn == "86D4EC90"
        assert settings.daily is True
        assert settings.weekly is False
        assert settings.monthly is True
        assert settings.alert_start == "8"
        assert settings.alert_end == "17"


@pytest.mark.asyncio
async def test_set_report_settings() -> None:
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/site/sn/report/setUp", payload=REPORT_SETUP_RESPONSE)

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            # Should not raise
            await client.set_report_settings(
                "86D4EC90",
                daily=True,
                weekly=True,
                monthly=True,
                alert_start="9",
                alert_end="18",
            )


@pytest.mark.asyncio
async def test_http_401_raises_auth_error() -> None:
    """HTTP-level 401 (empty body, e.g. session invalidated) raises NepAuthError."""
    with aioresponses() as m:
        _mock_sign_in(m)
        m.post(f"{BASE}/device/list", status=401, body="")

        async with ClientSession() as session:
            client = NepViewer(session, "test@example.com", "password")
            with pytest.raises(NepAuthError, match="HTTP 401"):
                await client.get_devices()


def test_sign_header_computed() -> None:
    """Verify that the sign header is MD5(body).upper()."""
    from aionepviewer.auth import NepAuth

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