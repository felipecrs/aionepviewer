"""Main client for the NEP solar inverter cloud API."""

from __future__ import annotations

from typing import Any

import aiohttp

from .auth import NepAuth
from .const import DEFAULT_HOST
from .models import (
    AccountInfo,
    AuthData,
    ChartData,
    ChartType,
    DateStatistics,
    DateStatisticsType,
    Device,
    DeviceDetail,
    DeviceStatisticsOverview,
    DeviceWifiOta,
    OverviewData,
    PlaybackData,
    PlaybackType,
    PowerParameter,
    ProductInfo,
    ReportSettings,
    Site,
    SiteDetail,
    SiteLayout,
    SiteModulesData,
    SiteOverview,
    SiteStatusCounts,
    Weather,
)


class NepViewer:
    """Async client for the NEP solar inverter cloud API (nepviewer.net).

    Designed to be used as a library for Home Assistant integrations.
    The caller provides an ``aiohttp.ClientSession`` (for connection pooling
    and SSL configuration) and account credentials.

    Parameters
    ----------
    session:
        An ``aiohttp.ClientSession`` instance.  The caller is responsible
        for creating and closing it.
    email:
        NEP account email address.
    password:
        NEP account password.
    host:
        Base URL for the API (default: ``https://api.nepviewer.net``).

    Example
    -------
    ::

        async with aiohttp.ClientSession() as session:
            client = NepViewer(session, "user@example.com", "password")
            auth = await client.authenticate()
            sites = await client.get_sites()
            for site in sites:
                overview = await client.get_site_overview(site.sid)
                print(overview.production.today)

    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        email: str,
        password: str,
        host: str = DEFAULT_HOST,
    ) -> None:
        self._auth = NepAuth(session, email, password, host)

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> AuthData:
        """Sign in and return user/token information.

        This must be called at least once before other API methods.
        Subsequent calls re-authenticate (useful for token refresh).
        """
        return await self._auth.sign_in()

    async def logout(self) -> None:
        """Explicitly log out and invalidate the current session token.

        After calling this, the token is cleared and any subsequent API
        calls will trigger a re-authentication.
        """
        await self._auth.request("POST", "/account/loginOut")
        self._auth._token_info = None

    async def get_account_info(self) -> AccountInfo:
        """Get detailed profile information for the current user.

        Returns contact details, location, group membership, and OEM info.
        """
        data = await self._auth.request("POST", "/account/info")
        return AccountInfo.from_dict(data)

    # ------------------------------------------------------------------
    # Global Overview
    # ------------------------------------------------------------------

    async def get_overview(self) -> OverviewData:
        """Get the global overview for all sites (production, benefit, counts)."""
        data = await self._auth.request("POST", "/overview/overview")
        return OverviewData.from_dict(data)

    async def get_site_status_counts(self) -> SiteStatusCounts:
        """Get the count of sites by online/offline status."""
        data = await self._auth.request("POST", "/overview/siteStatusCounts")
        return SiteStatusCounts.from_dict(data)

    # ------------------------------------------------------------------
    # Device List
    # ------------------------------------------------------------------

    async def get_devices(
        self,
        *,
        page_size: int = 100,
        page_num: int = 0,
        keywords: str = "",
        sn: str = "",
        site_name: str = "",
        status: str = "",
    ) -> list[Device]:
        """Get the list of all devices (gateways/microinverters).

        Parameters
        ----------
        page_size:
            Number of results per page.
        page_num:
            Page number (0-indexed).
        keywords:
            Search keywords filter.
        sn:
            Filter by serial number.
        site_name:
            Filter by site name.
        status:
            Filter by status.

        Returns
        -------
        list[Device]
            The list of devices.
        """
        body: dict[str, Any] = {
            "page": {"size": page_size, "num": page_num},
            "filters": {
                "keywords": keywords,
                "sn": sn,
                "site_name": site_name,
                "user_email": "",
                "installer_email": "",
                "is_commission": "",
                "model": "null",
                "country_code": "",
                "street": "",
                "status": status,
            },
            "sort": [],
        }
        data = await self._auth.request("POST", "/device/list", json_body=body)
        return [Device.from_dict(d) for d in data.get("list", [])]

    # ------------------------------------------------------------------
    # Device Detail & Statistics
    # ------------------------------------------------------------------

    async def get_device_detail(self, sid: str, sn: str) -> DeviceDetail:
        """Get detailed information for a specific device.

        Parameters
        ----------
        sid:
            Site ID.
        sn:
            Device serial number.
        """
        data = await self._auth.request(
            "POST", "/device/detail", json_body={"sid": sid, "sn": sn}
        )
        return DeviceDetail.from_dict(data)

    async def get_device_statistics_overview(self, sn: str) -> DeviceStatisticsOverview:
        """Get production, benefit, energy flow, and status for a device.

        This is the primary endpoint for device-level sensors in Home Assistant.
        """
        data = await self._auth.request(
            "POST", "/device/statistics/overview", json_body={"sn": sn}
        )
        return DeviceStatisticsOverview.from_dict(data)

    async def get_device_power_parameters(self, sn: str) -> list[PowerParameter]:
        """Get the list of available power parameters for a device.

        Returns names like "Production", "AC Voltage", "AC Frequency",
        "Temperature", "Power_1", "DC Voltage_1", etc.
        """
        data = await self._auth.request(
            "POST", "/device/powerParamateMap", json_body={"sn": sn}
        )
        return [PowerParameter.from_dict(p) for p in data.get("list", [])]

    async def get_device_statistics_chart(
        self,
        sn: str,
        chart_type: ChartType,
        *,
        date: str = "",
        range_date: str = "",
        weather_hours: bool = False,
        min_interval: int = 1,
        lines: list[str] | None = None,
    ) -> ChartData:
        """Get chart data for a device.

        Parameters
        ----------
        sn:
            Device serial number.
        chart_type:
            The chart granularity (DAY, DAILY, MONTHLY, YEARLY, INTRADAY_POWER).
        date:
            Date string.  Format depends on chart_type:
            - DAY/INTRADAY_POWER: ``"YYYY-MM-DD"``
            - MONTHLY: ``"YYYY-MM"`` (unused for some types)
        range_date:
            Date range for DAILY type: ``"YYYY-MM-DD~YYYY-MM-DD"``.
        weather_hours:
            Include weather data in the chart.
        min_interval:
            Minimum data interval (for DAY type).
        lines:
            List of parameter names to include (for DAY type, e.g. ``["Production"]``).
        """
        body: dict[str, Any] = {"types": int(chart_type), "sn": sn}
        if date:
            body["date"] = date
        if range_date:
            body["rangeDate"] = range_date
        if chart_type in (ChartType.DAY, ChartType.INTRADAY_POWER):
            body["weatherHours"] = weather_hours
        if chart_type == ChartType.DAY:
            body["minInterval"] = min_interval
            if lines:
                body["lines"] = lines
        data = await self._auth.request(
            "POST", "/device/statistics/echarts", json_body=body
        )
        return ChartData.from_dict(data)

    async def get_device_date_statistics(
        self,
        sn: str,
        stat_type: DateStatisticsType,
        date: str,
    ) -> DateStatistics:
        """Get power/consumption/economic statistics for a date period.

        Parameters
        ----------
        sn:
            Device serial number.
        stat_type:
            DAY (date format ``"YYYY-MM-DD"``) or MONTH (``"YYYY-MM"``).
        date:
            The date string matching the stat_type format.
        """
        data = await self._auth.request(
            "POST",
            "/device/statistics/date",
            json_body={"types": int(stat_type), "date": date, "sn": sn},
        )
        return DateStatistics.from_dict(data)

    async def get_device_playback(
        self,
        sn: str,
        start: str,
        end: str,
        playback_type: PlaybackType = PlaybackType.POWER,
    ) -> PlaybackData:
        """Get 5-minute interval playback data with per-module breakdown.

        Parameters
        ----------
        sn:
            Device serial number.
        start:
            Start date (``"YYYY-MM-DD"``).
        end:
            End date (``"YYYY-MM-DD"``).
        playback_type:
            The type of playback data.
        """
        data = await self._auth.request(
            "POST",
            "/device/playback",
            json_body={
                "sn": sn,
                "types": int(playback_type),
                "start": start,
                "end": end,
            },
        )
        return PlaybackData.from_dict(data)

    # ------------------------------------------------------------------
    # Site List
    # ------------------------------------------------------------------

    async def get_sites(
        self,
        *,
        page_size: int = 100,
        page_num: int = 0,
        keywords: str = "",
        site_name: str = "",
    ) -> list[Site]:
        """Get the list of all sites with their device (SN) details.

        Parameters
        ----------
        page_size:
            Number of results per page.
        page_num:
            Page number (0-indexed).
        keywords:
            Search keywords filter.
        site_name:
            Filter by site name.

        Returns
        -------
        list[Site]
            The list of sites.
        """
        body: dict[str, Any] = {
            "page": {"size": page_size, "num": page_num},
            "filters": {
                "keywords": keywords,
                "site_name": site_name,
                "user_email": "",
                "installer_email": "",
                "country_code": "",
                "created_start_date": "",
                "created_end_date": "",
                "street": "",
            },
            "sort": [],
        }
        data = await self._auth.request("POST", "/site/listWithSN", json_body=body)
        return [Site.from_dict(s) for s in data.get("list", [])]

    # ------------------------------------------------------------------
    # Site Detail & Overview
    # ------------------------------------------------------------------

    async def get_site_detail(self, sid: str) -> SiteDetail:
        """Get detailed information for a specific site.

        Parameters
        ----------
        sid:
            Site ID (e.g. ``"BR_20260317_tXFI"``).
        """
        data = await self._auth.request(
            "POST", "/site/detail", json_body={"sid": sid}
        )
        return SiteDetail.from_dict(data)

    async def get_site_overview(self, sid: str) -> SiteOverview:
        """Get the site overview including production, energy flow, and devices.

        This is the primary endpoint for site-level sensors in Home Assistant.
        """
        data = await self._auth.request(
            "POST", "/site/overview", json_body={"sid": sid}
        )
        return SiteOverview.from_dict(data)

    async def get_site_modules(self, sid: str, page: int = 0) -> SiteModulesData:
        """Get module-level (per-panel) data for a site.

        This returns individual microinverter module data grouped by device.

        Parameters
        ----------
        sid:
            Site ID.
        page:
            Module page number (for sites with many modules).
        """
        data = await self._auth.request(
            "POST", "/site/modules", json_body={"sid": sid, "page": page}
        )
        return SiteModulesData.from_dict(data)

    async def get_site_weather(self, sid: str) -> Weather:
        """Get the 7-day weather forecast for a site."""
        data = await self._auth.request(
            "POST", "/site/weather7Day", json_body={"sid": sid}
        )
        return Weather.from_dict(data)

    async def get_site_statistics_chart(
        self,
        sid: str,
        chart_type: ChartType,
        *,
        date: str = "",
        range_date: str = "",
        weather_hours: bool = False,
    ) -> ChartData:
        """Get chart data for a site.

        Parameters
        ----------
        sid:
            Site ID.
        chart_type:
            The chart granularity (DAY, DAILY, MONTHLY, YEARLY, INTRADAY_POWER).
        date:
            Date string (format depends on chart_type).
        range_date:
            Date range for DAILY type (``"YYYY-MM-DD~YYYY-MM-DD"``).
        weather_hours:
            Include weather data in the chart.
        """
        body: dict[str, Any] = {"types": int(chart_type), "sid": sid}
        if date:
            body["date"] = date
        if range_date:
            body["rangeDate"] = range_date
        if chart_type in (ChartType.DAY, ChartType.INTRADAY_POWER):
            body["weatherHours"] = weather_hours
        data = await self._auth.request(
            "POST", "/site/statistics/echarts", json_body=body
        )
        return ChartData.from_dict(data)

    async def get_site_layout(self, sid: str) -> SiteLayout:
        """Get the layout picture and scale for a site.

        Parameters
        ----------
        sid:
            Site ID.
        """
        data = await self._auth.request(
            "POST", "/site/layoutInfo", json_body={"sid": sid}
        )
        return SiteLayout.from_dict(data)

    # ------------------------------------------------------------------
    # Product Info
    # ------------------------------------------------------------------

    async def get_product_info(self, serial_numbers: list[str]) -> list[ProductInfo]:
        """Get product model and capability info for one or more serial numbers.

        Returns model name, supported functions (parameter settings, network
        config, power switching), and connectivity signals (MQTT, Bluetooth,
        AT command, AP).

        Parameters
        ----------
        serial_numbers:
            List of device serial numbers to look up.
        """
        data = await self._auth.request(
            "POST", "/product/sn/info", json_body={"sn": serial_numbers}
        )
        return [ProductInfo.from_dict(p) for p in data.get("list", [])]

    # ------------------------------------------------------------------
    # Device WiFi OTA
    # ------------------------------------------------------------------

    async def get_device_wifi_ota(
        self, devices: list[tuple[str, str]]
    ) -> list[DeviceWifiOta]:
        """Check WiFi firmware OTA status for one or more devices.

        Parameters
        ----------
        devices:
            List of ``(sn, wifi_version)`` tuples.  Pass an empty string
            for ``wifi_version`` to just query the current version.

        Returns
        -------
        list[DeviceWifiOta]
            OTA info per device, including current version and update advice.
        """
        payload = [{"sn": sn, "wifiVersion": ver} for sn, ver in devices]
        data = await self._auth.request(
            "POST", "/device/detailWifiOta", json_body={"wifiSn": payload}
        )
        # Response data is a list directly (not wrapped in a "list" key)
        if isinstance(data, list):
            return [DeviceWifiOta.from_dict(d) for d in data]
        return [DeviceWifiOta.from_dict(d) for d in data.get("list", [])]

    async def update_device_wifi_version(
        self, devices: list[tuple[str, str]]
    ) -> None:
        """Report the current WiFi firmware version for devices to the server.

        This is typically called by the Android app after connecting to a
        device to keep the server's firmware records up to date.

        Parameters
        ----------
        devices:
            List of ``(sn, wifi_version)`` tuples.
        """
        payload = [{"sn": sn, "wifiVersion": ver} for sn, ver in devices]
        await self._auth.request(
            "POST", "/device/updateWifiVersion", json_body={"wifiSn": payload}
        )

    # ------------------------------------------------------------------
    # Report Settings
    # ------------------------------------------------------------------

    async def get_report_settings(self, sid: str, sn: str) -> ReportSettings:
        """Get the email report notification settings for a device.

        Parameters
        ----------
        sid:
            Site ID.
        sn:
            Device serial number.
        """
        data = await self._auth.request(
            "POST",
            "/site/sn/report/settings",
            json_body={"sid": sid, "sn": sn},
        )
        return ReportSettings.from_dict(data)

    async def set_report_settings(
        self,
        sn: str,
        *,
        daily: bool = False,
        weekly: bool = False,
        monthly: bool = False,
        alert_start: str = "8",
        alert_end: str = "17",
    ) -> None:
        """Configure the email report notification settings for a device.

        Parameters
        ----------
        sn:
            Device serial number.
        daily:
            Enable daily production report email.
        weekly:
            Enable weekly production report email.
        monthly:
            Enable monthly production report email.
        alert_start:
            Alert monitoring window start hour (24h format string, e.g. ``"8"``).
        alert_end:
            Alert monitoring window end hour (24h format string, e.g. ``"17"``).
        """
        await self._auth.request(
            "POST",
            "/site/sn/report/setUp",
            json_body={
                "sn": sn,
                "optionsDaily": daily,
                "optionsWeekly": weekly,
                "optionsMonthly": monthly,
                "from": [alert_start, alert_end],
                "alertStart": alert_start,
                "alertEnd": alert_end,
            },
        )