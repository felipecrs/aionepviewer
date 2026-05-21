"""Device models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .alert import DeviceStatus
from .energy import EnergyFlow, EnvironmentalBenefit, ProductionStatistics


@dataclass(slots=True)
class Device:
    """A device (gateway/microinverter) from the device list."""

    sid: str
    sn: str
    status: int
    status_title: str
    alert_code: str
    alert_title: str
    alert_description: str
    model: int
    model_name: str
    last_update_time: int
    last_update: str
    last_update_cal: str
    created_at: str
    site_name: str
    country: str
    country_name: str
    state_name: str
    city: str
    street: str
    user_email: str
    installer_email: str
    commission_date: str
    now: float
    now_unit: str
    battery_soc: int
    wifi_version: str
    cpu_version: str
    ram_version: str
    alias: str

    @property
    def is_online(self) -> bool:
        return self.status == DeviceStatus.ONLINE

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Device:
        return cls(
            sid=data.get("sid", ""),
            sn=data.get("sn", ""),
            status=data.get("status", -1),
            status_title=data.get("statusTitle", "offline"),
            alert_code=data.get("alertCode", ""),
            alert_title=data.get("alertTitle", ""),
            alert_description=data.get("alertDescription", ""),
            model=data.get("model", 0),
            model_name=data.get("modelName", ""),
            last_update_time=data.get("lastUpdateTime", 0),
            last_update=data.get("lastUpdate", ""),
            last_update_cal=data.get("lastUpdateCal", ""),
            created_at=data.get("createdAt", ""),
            site_name=data.get("siteName", ""),
            country=data.get("country", ""),
            country_name=data.get("countryName", ""),
            state_name=data.get("stateName", ""),
            city=data.get("city", ""),
            street=data.get("street", ""),
            user_email=data.get("userEmail", ""),
            installer_email=data.get("installerEmail", ""),
            commission_date=data.get("commissionDate", ""),
            now=data.get("now", 0),
            now_unit=data.get("nowUnit", "W"),
            battery_soc=data.get("batterySoc", 0),
            wifi_version=data.get("WIFIVersion", ""),
            cpu_version=data.get("CPUVersion", ""),
            ram_version=data.get("RAMVersion", ""),
            alias=data.get("alias", ""),
        )


@dataclass(slots=True)
class DeviceDetail:
    """Detailed device information."""

    sid: str
    sn: str
    model_int: int
    model: str
    version: str
    model_title: str
    site_name: str
    country_name: str
    timezone: str
    user_email: str
    installer_email: str
    register_date: str
    is_commission: bool
    commission_date: str
    time: int
    temperature_unit: str
    currency_unit: str
    local_electric_price: float
    logo_full_path: str
    power_max: float
    country_code: str
    latitude: float
    longitude: float
    street: str
    city: str
    state_name: str
    wifi_version: str
    cpu_version: str
    ram_version: str
    alias: str
    connection_type: str
    system_type: int
    power_rating: float

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DeviceDetail:
        return cls(
            sid=data.get("sid", ""),
            sn=data.get("sn", ""),
            model_int=data.get("model_int", 0),
            model=data.get("model", ""),
            version=data.get("version", ""),
            model_title=data.get("modelTitle", ""),
            site_name=data.get("siteName", ""),
            country_name=data.get("countryName", ""),
            timezone=data.get("timezone", ""),
            user_email=data.get("userEmail", ""),
            installer_email=data.get("installerEmail", ""),
            register_date=data.get("registerDate", ""),
            is_commission=data.get("isCommission", False),
            commission_date=data.get("commissionDate", ""),
            time=data.get("time", 0),
            temperature_unit=data.get("temperatureUnit", "Celsius"),
            currency_unit=data.get("currency_unit", ""),
            local_electric_price=data.get("local_electric_price", 0),
            logo_full_path=data.get("logoFullPath", ""),
            power_max=data.get("powerMax", 0),
            country_code=data.get("countryCode", ""),
            latitude=data.get("latitude", 0),
            longitude=data.get("longitude", 0),
            street=data.get("street", ""),
            city=data.get("city", ""),
            state_name=data.get("stateName", ""),
            wifi_version=data.get("wifiVersion", ""),
            cpu_version=data.get("cpuVersion", ""),
            ram_version=data.get("ramVersion", ""),
            alias=data.get("alias", ""),
            connection_type=data.get("connectionType", ""),
            system_type=data.get("systemType", 0),
            power_rating=data.get("powerRating", 0),
        )


@dataclass(slots=True)
class DeviceStatisticsOverview:
    """Device statistics overview including production, benefit, and energy flow."""

    max_now: int
    total_now: float
    total_now_unit: str
    currency_unit: str
    local_electric_price: float
    production: ProductionStatistics
    environmental_benefit: EnvironmentalBenefit
    status: int
    status_title: str
    alert_code: str
    alert_title: str
    alert_description: str
    last_update: str
    last_update_cal: str
    last_update_time: int
    is_consumption: bool
    energy: EnergyFlow

    @property
    def is_online(self) -> bool:
        return self.status == DeviceStatus.ONLINE

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DeviceStatisticsOverview:
        return cls(
            max_now=data.get("maxNow", 0),
            total_now=data.get("totalNow", 0),
            total_now_unit=data.get("totalNowUnit", "W"),
            currency_unit=data.get("currency_unit", ""),
            local_electric_price=data.get("local_electric_price", 0),
            production=ProductionStatistics.from_api(data.get("production", {})),
            environmental_benefit=EnvironmentalBenefit.from_api(
                data.get("environmentalBenefit", {})
            ),
            status=data.get("status", -1),
            status_title=data.get("statusTitle", "offline"),
            alert_code=data.get("alertCode", ""),
            alert_title=data.get("alertTitle", ""),
            alert_description=data.get("alertDescription", ""),
            last_update=data.get("lastUpdate", ""),
            last_update_cal=data.get("lastUpdateCal", ""),
            last_update_time=data.get("lastUpdateTime", 0),
            is_consumption=data.get("isConsumption", False),
            energy=EnergyFlow.from_api(data.get("energy", {})),
        )


@dataclass(slots=True)
class PowerParameter:
    """A power parameter available for a device."""

    name: str
    unit: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PowerParameter:
        return cls(name=data["name"], unit=data["unit"])


@dataclass(slots=True)
class DeviceOverviewItem:
    """A device entry within the site overview response."""

    sid: str
    sn: str
    model: int
    model_name: str
    status: int
    status_title: str
    page_type: int
    now: str
    today: str
    now_unit: str
    today_unit: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DeviceOverviewItem:
        return cls(
            sid=data.get("sid", ""),
            sn=data.get("sn", ""),
            model=data.get("model", 0),
            model_name=data.get("modelName", ""),
            status=data.get("status", -1),
            status_title=data.get("statusTitle", "offline"),
            page_type=data.get("pageType", 0),
            now=data.get("now", "0"),
            today=data.get("today", "0"),
            now_unit=data.get("nowUnit", "W"),
            today_unit=data.get("todayUnit", "kWh"),
        )


@dataclass(slots=True)
class DeviceWifiOta:
    """WiFi firmware OTA status for a device."""

    sn: str
    wifi_version: str
    advice: int
    address: str

    @property
    def update_available(self) -> bool:
        """Return ``True`` if a firmware update is recommended (advice != 2)."""
        return self.advice != 2

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DeviceWifiOta:
        return cls(
            sn=data.get("sn", ""),
            wifi_version=data.get("wifiVersion", ""),
            advice=data.get("advice", 2),
            address=data.get("address", ""),
        )