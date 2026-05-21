"""Device models for the NEP API."""

from __future__ import annotations

from typing import Any

from .alert import DeviceStatus
from .energy import EnergyFlow, EnvironmentalBenefit, ProductionStatistics


class Device:
    """A device (gateway/microinverter) from the device list."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sid(self) -> str:
        return self.raw_data.get("sid", "")

    @property
    def sn(self) -> str:
        return self.raw_data.get("sn", "")

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
    def model(self) -> int:
        return self.raw_data.get("model", 0)

    @property
    def model_name(self) -> str:
        return self.raw_data.get("modelName", "")

    @property
    def last_update_time(self) -> int:
        return self.raw_data.get("lastUpdateTime", 0)

    @property
    def last_update(self) -> str:
        return self.raw_data.get("lastUpdate", "")

    @property
    def last_update_cal(self) -> str:
        return self.raw_data.get("lastUpdateCal", "")

    @property
    def created_at(self) -> str:
        return self.raw_data.get("createdAt", "")

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
    def commission_date(self) -> str:
        return self.raw_data.get("commissionDate", "")

    @property
    def now(self) -> float:
        return self.raw_data.get("now", 0)

    @property
    def now_unit(self) -> str:
        return self.raw_data.get("nowUnit", "W")

    @property
    def battery_soc(self) -> int:
        return self.raw_data.get("batterySoc", 0)

    @property
    def wifi_version(self) -> str:
        return self.raw_data.get("WIFIVersion", "")

    @property
    def cpu_version(self) -> str:
        return self.raw_data.get("CPUVersion", "")

    @property
    def ram_version(self) -> str:
        return self.raw_data.get("RAMVersion", "")

    @property
    def alias(self) -> str:
        return self.raw_data.get("alias", "")

    @property
    def is_online(self) -> bool:
        return self.status == DeviceStatus.ONLINE


class DeviceDetail:
    """Detailed device information."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sid(self) -> str:
        return self.raw_data.get("sid", "")

    @property
    def sn(self) -> str:
        return self.raw_data.get("sn", "")

    @property
    def model_int(self) -> int:
        return self.raw_data.get("model_int", 0)

    @property
    def model(self) -> str:
        return self.raw_data.get("model", "")

    @property
    def version(self) -> str:
        return self.raw_data.get("version", "")

    @property
    def model_title(self) -> str:
        return self.raw_data.get("modelTitle", "")

    @property
    def site_name(self) -> str:
        return self.raw_data.get("siteName", "")

    @property
    def country_name(self) -> str:
        return self.raw_data.get("countryName", "")

    @property
    def timezone(self) -> str:
        return self.raw_data.get("timezone", "")

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
    def time(self) -> int:
        return self.raw_data.get("time", 0)

    @property
    def temperature_unit(self) -> str:
        return self.raw_data.get("temperatureUnit", "Celsius")

    @property
    def currency_unit(self) -> str:
        return self.raw_data.get("currency_unit", "")

    @property
    def local_electric_price(self) -> float:
        return self.raw_data.get("local_electric_price", 0)

    @property
    def logo_full_path(self) -> str:
        return self.raw_data.get("logoFullPath", "")

    @property
    def power_max(self) -> float:
        return self.raw_data.get("powerMax", 0)

    @property
    def country_code(self) -> str:
        return self.raw_data.get("countryCode", "")

    @property
    def latitude(self) -> float:
        return self.raw_data.get("latitude", 0)

    @property
    def longitude(self) -> float:
        return self.raw_data.get("longitude", 0)

    @property
    def street(self) -> str:
        return self.raw_data.get("street", "")

    @property
    def city(self) -> str:
        return self.raw_data.get("city", "")

    @property
    def state_name(self) -> str:
        return self.raw_data.get("stateName", "")

    @property
    def wifi_version(self) -> str:
        return self.raw_data.get("wifiVersion", "")

    @property
    def cpu_version(self) -> str:
        return self.raw_data.get("cpuVersion", "")

    @property
    def ram_version(self) -> str:
        return self.raw_data.get("ramVersion", "")

    @property
    def alias(self) -> str:
        return self.raw_data.get("alias", "")

    @property
    def connection_type(self) -> str:
        return self.raw_data.get("connectionType", "")

    @property
    def system_type(self) -> int:
        return self.raw_data.get("systemType", 0)

    @property
    def power_rating(self) -> float:
        return self.raw_data.get("powerRating", 0)


class DeviceStatisticsOverview:
    """Device statistics overview including production, benefit, and energy flow."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def max_now(self) -> int:
        return self.raw_data.get("maxNow", 0)

    @property
    def total_now(self) -> float:
        return self.raw_data.get("totalNow", 0)

    @property
    def total_now_unit(self) -> str:
        return self.raw_data.get("totalNowUnit", "W")

    @property
    def currency_unit(self) -> str:
        return self.raw_data.get("currency_unit", "")

    @property
    def local_electric_price(self) -> float:
        return self.raw_data.get("local_electric_price", 0)

    @property
    def production(self) -> ProductionStatistics:
        return ProductionStatistics(self.raw_data.get("production", {}))

    @property
    def environmental_benefit(self) -> EnvironmentalBenefit:
        return EnvironmentalBenefit(self.raw_data.get("environmentalBenefit", {}))

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
    def is_consumption(self) -> bool:
        return self.raw_data.get("isConsumption", False)

    @property
    def energy(self) -> EnergyFlow:
        return EnergyFlow(self.raw_data.get("energy", {}))

    @property
    def is_online(self) -> bool:
        return self.status == DeviceStatus.ONLINE


class PowerParameter:
    """A power parameter available for a device."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def name(self) -> str:
        return self.raw_data["name"]

    @property
    def unit(self) -> str:
        return self.raw_data["unit"]


class DeviceOverviewItem:
    """A device entry within the site overview response."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sid(self) -> str:
        return self.raw_data.get("sid", "")

    @property
    def sn(self) -> str:
        return self.raw_data.get("sn", "")

    @property
    def model(self) -> int:
        return self.raw_data.get("model", 0)

    @property
    def model_name(self) -> str:
        return self.raw_data.get("modelName", "")

    @property
    def status(self) -> int:
        return self.raw_data.get("status", -1)

    @property
    def status_title(self) -> str:
        return self.raw_data.get("statusTitle", "offline")

    @property
    def page_type(self) -> int:
        return self.raw_data.get("pageType", 0)

    @property
    def now(self) -> str:
        return self.raw_data.get("now", "0")

    @property
    def today(self) -> str:
        return self.raw_data.get("today", "0")

    @property
    def now_unit(self) -> str:
        return self.raw_data.get("nowUnit", "W")

    @property
    def today_unit(self) -> str:
        return self.raw_data.get("todayUnit", "kWh")


class DeviceWifiOta:
    """WiFi firmware OTA status for a device."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sn(self) -> str:
        return self.raw_data.get("sn", "")

    @property
    def wifi_version(self) -> str:
        return self.raw_data.get("wifiVersion", "")

    @property
    def advice(self) -> int:
        return self.raw_data.get("advice", 2)

    @property
    def address(self) -> str:
        return self.raw_data.get("address", "")

    @property
    def update_available(self) -> bool:
        """Return ``True`` if a firmware update is recommended (advice != 2)."""
        return self.advice != 2