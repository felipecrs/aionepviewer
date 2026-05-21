"""Site models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .alert import AlertInfo, DeviceStatus
from .device import DeviceOverviewItem
from .energy import EnergyFlow, EnvironmentalBenefit, ProductionStatistics


@dataclass(slots=True)
class SiteDeviceSummary:
    """Summary of a device within a site listing."""

    sid: str
    sn: str
    model: str
    status: int
    status_title: str
    alert_code: str
    alert_title: str
    alert_description: str
    last_update: str
    last_update_cal: str
    last_update_time: int
    now: float
    today_power: float
    total_power: float
    now_unit: str
    today_power_unit: str
    total_power_unit: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiteDeviceSummary:
        return cls(
            sid=data.get("sid", ""),
            sn=data.get("sn", ""),
            model=data.get("model", ""),
            status=data.get("status", -1),
            status_title=data.get("statusTitle", "offline"),
            alert_code=data.get("alertCode", ""),
            alert_title=data.get("alertTitle", ""),
            alert_description=data.get("alertDescription", ""),
            last_update=data.get("lastUpdate", ""),
            last_update_cal=data.get("lastUpdateCal", ""),
            last_update_time=data.get("lastUpdateTime", 0),
            now=data.get("now", 0),
            today_power=data.get("todayPower", 0),
            total_power=data.get("totalPower", 0),
            now_unit=data.get("nowUnit", "W"),
            today_power_unit=data.get("todayPowerUnit", "kWh"),
            total_power_unit=data.get("totalPowerUnit", "kWh"),
        )


@dataclass(slots=True)
class Site:
    """A site from the site list (with SN details)."""

    sid: str
    site_name: str
    country: str
    country_name: str
    state_name: str
    city: str
    street: str
    user_email: str
    installer_email: str
    register_date: str
    is_commission: bool
    commission_date: str
    sn_count: int
    devices: list[SiteDeviceSummary]
    status: int
    status_title: str
    logo: str
    now: float
    today_power: float
    total_power: float
    now_unit: str
    today_power_unit: str
    total_power_unit: str
    last_update: str
    last_update_cal: str
    last_update_time: int

    @property
    def is_online(self) -> bool:
        return self.status == DeviceStatus.ONLINE

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Site:
        return cls(
            sid=data.get("sid", ""),
            site_name=data.get("siteName", ""),
            country=data.get("country", ""),
            country_name=data.get("countryName", ""),
            state_name=data.get("stateName", ""),
            city=data.get("city", ""),
            street=data.get("street", ""),
            user_email=data.get("userEmail", ""),
            installer_email=data.get("installerEmail", ""),
            register_date=data.get("registerDate", ""),
            is_commission=data.get("isCommission", False),
            commission_date=data.get("commissionDate", ""),
            sn_count=data.get("snCount", 0),
            devices=[SiteDeviceSummary.from_api(d) for d in data.get("sn", [])],
            status=data.get("status", -1),
            status_title=data.get("statusTitle", "offline"),
            logo=data.get("logo", ""),
            now=data.get("now", 0),
            today_power=data.get("todayPower", 0),
            total_power=data.get("totalPower", 0),
            now_unit=data.get("nowUnit", "W"),
            today_power_unit=data.get("todayPowerUnit", "kWh"),
            total_power_unit=data.get("totalPowerUnit", "kWh"),
            last_update=data.get("lastUpdate", ""),
            last_update_cal=data.get("lastUpdateCal", ""),
            last_update_time=data.get("lastUpdateTime", 0),
        )


@dataclass(slots=True)
class SiteDetail:
    """Detailed site information."""

    sid: str
    site_name: str
    country_code: str
    country_name: str
    state_code: str
    state_name: str
    city: str
    street: str
    zip_code: str
    timezone: str
    latitude: float
    longitude: float
    logo: str
    logo_full_path: str
    commission: int
    register_date: str
    commission_date: str
    currency: str
    electricity_price: float
    temperature_unit: str
    pv_remark: str
    battery_remark: str
    user_email: str
    installer_email: str
    power_max: float
    company_id: int
    company_name: str
    ownership_type: int
    system_type: int
    connection_type: str
    panel_model: str
    panel_type: str
    power_rating: float
    sn_list: list[dict[str, Any]]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiteDetail:
        return cls(
            sid=data.get("sid", ""),
            site_name=data.get("siteName", ""),
            country_code=data.get("countryCode", ""),
            country_name=data.get("countryName", ""),
            state_code=data.get("stateCode", ""),
            state_name=data.get("stateName", ""),
            city=data.get("city", ""),
            street=data.get("street", ""),
            zip_code=data.get("zipCode", ""),
            timezone=data.get("timezone", ""),
            latitude=data.get("latitude", 0),
            longitude=data.get("longitude", 0),
            logo=data.get("logo", ""),
            logo_full_path=data.get("logoFullPath", ""),
            commission=data.get("commission", 0),
            register_date=data.get("registerDate", ""),
            commission_date=data.get("commissionDate", ""),
            currency=data.get("currency", ""),
            electricity_price=data.get("electricityPrice", 0),
            temperature_unit=data.get("temperatureUnit", "Celsius"),
            pv_remark=data.get("pvRemark", ""),
            battery_remark=data.get("batteryRemark", ""),
            user_email=data.get("userEmail", ""),
            installer_email=data.get("installerEmail", ""),
            power_max=data.get("powerMax", 0),
            company_id=data.get("companyId", 0),
            company_name=data.get("companyName", ""),
            ownership_type=data.get("ownershipType", 0),
            system_type=data.get("systemType", 0),
            connection_type=data.get("connectionType", ""),
            panel_model=data.get("model", ""),
            panel_type=data.get("panelType", ""),
            power_rating=data.get("powerRating", 0),
            sn_list=data.get("sn", []),
        )


@dataclass(slots=True)
class SiteOverview:
    """Site overview data including production, benefit, energy flow, devices."""

    production: ProductionStatistics
    benefit: EnvironmentalBenefit
    status: int
    status_title: str
    last_update_cal: str
    last_update: str
    created_at: str
    device_list: list[DeviceOverviewItem]
    energy: EnergyFlow
    alert: AlertInfo
    max_power: int
    components: list[str]

    @property
    def is_online(self) -> bool:
        return self.status == DeviceStatus.ONLINE

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiteOverview:
        return cls(
            production=ProductionStatistics.from_api(
                data.get("statisticsProduction", {})
            ),
            benefit=EnvironmentalBenefit.from_api(data.get("benefit", {})),
            status=data.get("status", -1),
            status_title=data.get("statusTitle", "offline"),
            last_update_cal=data.get("lastUpdateCal", ""),
            last_update=data.get("lastUpdate", ""),
            created_at=data.get("createdAt", ""),
            device_list=[
                DeviceOverviewItem.from_api(d) for d in data.get("deviceList", [])
            ],
            energy=EnergyFlow.from_api(data.get("energy", {})),
            alert=AlertInfo.from_api(data.get("alert", {})),
            max_power=data.get("max_power", 0),
            components=data.get("components", []),
        )


@dataclass(slots=True)
class SiteLayout:
    """Site layout picture and scale information."""

    sid: str
    site_name: str
    layout_pic: str
    layout_scale: float

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiteLayout:
        return cls(
            sid=data.get("sid", ""),
            site_name=data.get("siteName", ""),
            layout_pic=data.get("layoutPic", ""),
            layout_scale=data.get("layoutScale", 0),
        )


@dataclass(slots=True)
class SiteStatusCounts:
    """Site status distribution from /overview/siteStatusCounts."""

    site_count: int
    status_map: dict[str, int]

    @property
    def online_count(self) -> int:
        return self.status_map.get("0", 0)

    @property
    def offline_count(self) -> int:
        return self.status_map.get("-1", 0)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiteStatusCounts:
        return cls(
            site_count=data.get("siteCount", 0),
            status_map=data.get("statusMap", {}),
        )