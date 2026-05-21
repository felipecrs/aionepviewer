"""Site models for the NEP API."""

from __future__ import annotations

from typing import Any

from .alert import AlertInfo, DeviceStatus
from .device import DeviceOverviewItem
from .energy import EnergyFlow, EnvironmentalBenefit, ProductionStatistics


class SiteDeviceSummary:
    """Summary of a device within a site listing."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sid(self) -> str:
        return self.raw_data.get("sid", "")

    @property
    def sn(self) -> str:
        return self.raw_data.get("sn", "").upper()

    @property
    def model(self) -> str:
        return self.raw_data.get("model", "")

    @property
    def status(self) -> int:
        return self.raw_data.get("status", -1)

    @property
    def status_title(self) -> str:
        return self.raw_data.get("statusTitle", "offline")

    @property
    def alert_code(self) -> str:
        return self.raw_data.get("alertCode", "")

    @property
    def alert_title(self) -> str:
        return self.raw_data.get("alertTitle", "")

    @property
    def alert_description(self) -> str:
        return self.raw_data.get("alertDescription", "")

    @property
    def last_update(self) -> str:
        return self.raw_data.get("lastUpdate", "")

    @property
    def last_update_cal(self) -> str:
        return self.raw_data.get("lastUpdateCal", "")

    @property
    def last_update_time(self) -> int:
        return self.raw_data.get("lastUpdateTime", 0)

    @property
    def now(self) -> float:
        return self.raw_data.get("now", 0)

    @property
    def today_power(self) -> float:
        return self.raw_data.get("todayPower", 0)

    @property
    def total_power(self) -> float:
        return self.raw_data.get("totalPower", 0)

    @property
    def now_unit(self) -> str:
        return self.raw_data.get("nowUnit", "W")

    @property
    def today_power_unit(self) -> str:
        return self.raw_data.get("todayPowerUnit", "kWh")

    @property
    def total_power_unit(self) -> str:
        return self.raw_data.get("totalPowerUnit", "kWh")


class Site:
    """A site from the site list (with SN details)."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sid(self) -> str:
        return self.raw_data.get("sid", "")

    @property
    def site_name(self) -> str:
        return self.raw_data.get("siteName", "")

    @property
    def country(self) -> str:
        return self.raw_data.get("country", "")

    @property
    def country_name(self) -> str:
        return self.raw_data.get("countryName", "")

    @property
    def state_name(self) -> str:
        return self.raw_data.get("stateName", "")

    @property
    def city(self) -> str:
        return self.raw_data.get("city", "")

    @property
    def street(self) -> str:
        return self.raw_data.get("street", "")

    @property
    def user_email(self) -> str:
        return self.raw_data.get("userEmail", "")

    @property
    def installer_email(self) -> str:
        return self.raw_data.get("installerEmail", "")

    @property
    def register_date(self) -> str:
        return self.raw_data.get("registerDate", "")

    @property
    def is_commission(self) -> bool:
        return self.raw_data.get("isCommission", False)

    @property
    def commission_date(self) -> str:
        return self.raw_data.get("commissionDate", "")

    @property
    def sn_count(self) -> int:
        return self.raw_data.get("snCount", 0)

    @property
    def devices(self) -> list[SiteDeviceSummary]:
        return [SiteDeviceSummary(d) for d in self.raw_data.get("sn", [])]

    @property
    def status(self) -> int:
        return self.raw_data.get("status", -1)

    @property
    def status_title(self) -> str:
        return self.raw_data.get("statusTitle", "offline")

    @property
    def logo(self) -> str:
        return self.raw_data.get("logo", "")

    @property
    def now(self) -> float:
        return self.raw_data.get("now", 0)

    @property
    def today_power(self) -> float:
        return self.raw_data.get("todayPower", 0)

    @property
    def total_power(self) -> float:
        return self.raw_data.get("totalPower", 0)

    @property
    def now_unit(self) -> str:
        return self.raw_data.get("nowUnit", "W")

    @property
    def today_power_unit(self) -> str:
        return self.raw_data.get("todayPowerUnit", "kWh")

    @property
    def total_power_unit(self) -> str:
        return self.raw_data.get("totalPowerUnit", "kWh")

    @property
    def last_update(self) -> str:
        return self.raw_data.get("lastUpdate", "")

    @property
    def last_update_cal(self) -> str:
        return self.raw_data.get("lastUpdateCal", "")

    @property
    def last_update_time(self) -> int:
        return self.raw_data.get("lastUpdateTime", 0)

    @property
    def is_online(self) -> bool:
        return self.status == DeviceStatus.ONLINE


class SiteDetail:
    """Detailed site information."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sid(self) -> str:
        return self.raw_data.get("sid", "")

    @property
    def site_name(self) -> str:
        return self.raw_data.get("siteName", "")

    @property
    def country_code(self) -> str:
        return self.raw_data.get("countryCode", "")

    @property
    def country_name(self) -> str:
        return self.raw_data.get("countryName", "")

    @property
    def state_code(self) -> str:
        return self.raw_data.get("stateCode", "")

    @property
    def state_name(self) -> str:
        return self.raw_data.get("stateName", "")

    @property
    def city(self) -> str:
        return self.raw_data.get("city", "")

    @property
    def street(self) -> str:
        return self.raw_data.get("street", "")

    @property
    def zip_code(self) -> str:
        return self.raw_data.get("zipCode", "")

    @property
    def timezone(self) -> str:
        return self.raw_data.get("timezone", "")

    @property
    def latitude(self) -> float:
        return self.raw_data.get("latitude", 0)

    @property
    def longitude(self) -> float:
        return self.raw_data.get("longitude", 0)

    @property
    def logo(self) -> str:
        return self.raw_data.get("logo", "")

    @property
    def logo_full_path(self) -> str:
        return self.raw_data.get("logoFullPath", "")

    @property
    def commission(self) -> int:
        return self.raw_data.get("commission", 0)

    @property
    def register_date(self) -> str:
        return self.raw_data.get("registerDate", "")

    @property
    def commission_date(self) -> str:
        return self.raw_data.get("commissionDate", "")

    @property
    def currency(self) -> str:
        return self.raw_data.get("currency", "")

    @property
    def electricity_price(self) -> float:
        return self.raw_data.get("electricityPrice", 0)

    @property
    def temperature_unit(self) -> str:
        return self.raw_data.get("temperatureUnit", "Celsius")

    @property
    def pv_remark(self) -> str:
        return self.raw_data.get("pvRemark", "")

    @property
    def battery_remark(self) -> str:
        return self.raw_data.get("batteryRemark", "")

    @property
    def user_email(self) -> str:
        return self.raw_data.get("userEmail", "")

    @property
    def installer_email(self) -> str:
        return self.raw_data.get("installerEmail", "")

    @property
    def power_max(self) -> float:
        return self.raw_data.get("powerMax", 0)

    @property
    def company_id(self) -> int:
        return self.raw_data.get("companyId", 0)

    @property
    def company_name(self) -> str:
        return self.raw_data.get("companyName", "")

    @property
    def ownership_type(self) -> int:
        return self.raw_data.get("ownershipType", 0)

    @property
    def system_type(self) -> int:
        return self.raw_data.get("systemType", 0)

    @property
    def connection_type(self) -> str:
        return self.raw_data.get("connectionType", "")

    @property
    def panel_model(self) -> str:
        return self.raw_data.get("model", "")

    @property
    def panel_type(self) -> str:
        return self.raw_data.get("panelType", "")

    @property
    def power_rating(self) -> float:
        return self.raw_data.get("powerRating", 0)

    @property
    def sn_list(self) -> list[dict[str, Any]]:
        return self.raw_data.get("sn", [])


class SiteOverview:
    """Site overview data including production, benefit, energy flow, devices."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def production(self) -> ProductionStatistics:
        return ProductionStatistics(self.raw_data.get("statisticsProduction", {}))

    @property
    def benefit(self) -> EnvironmentalBenefit:
        return EnvironmentalBenefit(self.raw_data.get("benefit", {}))

    @property
    def status(self) -> int:
        return self.raw_data.get("status", -1)

    @property
    def status_title(self) -> str:
        return self.raw_data.get("statusTitle", "offline")

    @property
    def last_update_cal(self) -> str:
        return self.raw_data.get("lastUpdateCal", "")

    @property
    def last_update(self) -> str:
        return self.raw_data.get("lastUpdate", "")

    @property
    def created_at(self) -> str:
        return self.raw_data.get("createdAt", "")

    @property
    def device_list(self) -> list[DeviceOverviewItem]:
        return [DeviceOverviewItem(d) for d in self.raw_data.get("deviceList", [])]

    @property
    def energy(self) -> EnergyFlow:
        return EnergyFlow(self.raw_data.get("energy", {}))

    @property
    def alert(self) -> AlertInfo:
        return AlertInfo(self.raw_data.get("alert", {}))

    @property
    def max_power(self) -> int:
        return self.raw_data.get("max_power", 0)

    @property
    def components(self) -> list[str]:
        return self.raw_data.get("components", [])

    @property
    def is_online(self) -> bool:
        return self.status == DeviceStatus.ONLINE


class SiteLayout:
    """Site layout picture and scale information."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sid(self) -> str:
        return self.raw_data.get("sid", "")

    @property
    def site_name(self) -> str:
        return self.raw_data.get("siteName", "")

    @property
    def layout_pic(self) -> str:
        return self.raw_data.get("layoutPic", "")

    @property
    def layout_scale(self) -> float:
        return self.raw_data.get("layoutScale", 0)


class SiteStatusCounts:
    """Site status distribution from /overview/siteStatusCounts."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def site_count(self) -> int:
        return self.raw_data.get("siteCount", 0)

    @property
    def status_map(self) -> dict[str, int]:
        return self.raw_data.get("statusMap", {})

    @property
    def online_count(self) -> int:
        return self.status_map.get("0", 0)

    @property
    def offline_count(self) -> int:
        return self.status_map.get("-1", 0)