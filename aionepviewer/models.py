"""Data models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ChartType(IntEnum):
    """Chart granularity types for statistics/echarts endpoints."""

    DAY = 1  # Intraday data (configurable interval)
    DAILY = 3  # Daily bars within a date range
    MONTHLY = 5  # Monthly bars
    YEARLY = 6  # Yearly bars (months on x-axis)
    INTRADAY_POWER = 11  # Intraday AC output power (15-min intervals)


class DateStatisticsType(IntEnum):
    """Period types for the device/statistics/date endpoint."""

    DAY = 1  # Daily (date format: YYYY-MM-DD)
    MONTH = 2  # Monthly (date format: YYYY-MM)


class PlaybackType(IntEnum):
    """Playback data types for the device/playback endpoint."""

    POWER = 1  # Power playback (5-min intervals, full day)


class DeviceStatus(IntEnum):
    """Device online/offline status."""

    ONLINE = 0
    OFFLINE = -1


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


@dataclass
class UserInfo:
    """User information returned after sign-in."""

    uid: str
    email: str
    country: str
    state: str
    role: int
    group_id: int
    group_name: str
    header_img: str
    default_area: str
    company_id: int
    is_company_owner: int
    oem_id: int
    oem_web: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserInfo:
        return cls(
            uid=data["uid"],
            email=data["email"],
            country=data.get("country", ""),
            state=data.get("state", ""),
            role=data.get("role", 0),
            group_id=data.get("groupId", 0),
            group_name=data.get("groupName", ""),
            header_img=data.get("headerImg", ""),
            default_area=data.get("defaultArea", ""),
            company_id=data.get("companyId", 0),
            is_company_owner=data.get("isCompanyOwner", 0),
            oem_id=data.get("oemid", 0),
            oem_web=data.get("oemweb", ""),
        )


@dataclass
class TokenInfo:
    """JWT token information."""

    token: str
    expires_at: int
    duration: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TokenInfo:
        return cls(
            token=data["token"],
            expires_at=data["expiresAt"],
            duration=data.get("duration", 43200),
        )


@dataclass
class AuthData:
    """Combined authentication data from sign-in."""

    user_info: UserInfo
    token_info: TokenInfo
    site_count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuthData:
        return cls(
            user_info=UserInfo.from_dict(data["userInfo"]),
            token_info=TokenInfo.from_dict(data["tokenInfo"]),
            site_count=data.get("siteCount", 0),
        )


# ---------------------------------------------------------------------------
# Energy Flow
# ---------------------------------------------------------------------------


@dataclass
class EnergySource:
    """A single energy source in the energy flow diagram."""

    power: float
    power_unit: str
    direction: int
    show: bool
    rate: float
    show_power: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EnergySource:
        return cls(
            power=data.get("power", 0),
            power_unit=data.get("powerUnit", "W"),
            direction=data.get("direction", 0),
            show=data.get("show", False),
            rate=data.get("rate", 0),
            show_power=data.get("showPower", False),
        )


@dataclass
class EnergyFlow:
    """Energy flow diagram data (PV → home, grid, battery, gen)."""

    pv_panel: EnergySource
    home: EnergySource
    grid: EnergySource
    battery: EnergySource
    generator: EnergySource

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EnergyFlow:
        return cls(
            pv_panel=EnergySource.from_dict(data.get("PVPanel", {})),
            home=EnergySource.from_dict(data.get("home", {})),
            grid=EnergySource.from_dict(data.get("grid", {})),
            battery=EnergySource.from_dict(data.get("battery", {})),
            generator=EnergySource.from_dict(data.get("gen", {})),
        )


# ---------------------------------------------------------------------------
# Production & Environmental Benefit
# ---------------------------------------------------------------------------


@dataclass
class ProductionStatistics:
    """Energy production statistics."""

    today: str
    today_unit: str
    yesterday: str
    yesterday_unit: str
    month: str
    month_unit: str
    year: str
    year_unit: str
    total: str
    total_unit: str
    total_now: str
    total_now_unit: str
    total_money: str
    today_money: str
    yesterday_money: str
    month_money: str
    total_money_unit: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProductionStatistics:
        return cls(
            today=data.get("today", "0"),
            today_unit=data.get("todayUnit", "kWh"),
            yesterday=data.get("yesterday", "0"),
            yesterday_unit=data.get("yesterdayUnit", "kWh"),
            month=data.get("month", "0"),
            month_unit=data.get("monthUnit", "kWh"),
            year=data.get("year", "0"),
            year_unit=data.get("yearUnit", "kWh"),
            total=data.get("total", "0"),
            total_unit=data.get("totalUnit", "kWh"),
            total_now=data.get("totalNow", "0"),
            total_now_unit=data.get("totalNowUnit", "W"),
            total_money=data.get("totalMoney", "0"),
            today_money=data.get("todayMoney", "0"),
            yesterday_money=data.get("yesterdayMoney", "0"),
            month_money=data.get("monthMoney", "0"),
            total_money_unit=data.get("totalMoneyUnit", ""),
        )


@dataclass
class EnvironmentalBenefit:
    """Environmental benefit metrics."""

    co2: str
    co2_unit: str
    tree: str
    tree_unit: str
    car: str
    car_unit: str
    light: str
    light_unit: str
    oil: str
    oil_unit: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EnvironmentalBenefit:
        return cls(
            co2=data.get("co2", "0"),
            co2_unit=data.get("co2Unit", "kg"),
            tree=data.get("tree", "0"),
            tree_unit=data.get("treeUnit", "Trees"),
            car=data.get("car", "0"),
            car_unit=data.get("carUnit", "km"),
            light=data.get("light", "0"),
            light_unit=data.get("lightUnit", "H"),
            oil=data.get("oil", "0"),
            oil_unit=data.get("oilUnit", "BBL"),
        )


# ---------------------------------------------------------------------------
# Alert
# ---------------------------------------------------------------------------


@dataclass
class AlertInfo:
    """Alert information for a device or site."""

    code: str
    title: str
    description: str

    @property
    def is_ok(self) -> bool:
        return self.code == "0000"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlertInfo:
        return cls(
            code=data.get("code", data.get("alertCode", "0000")),
            title=data.get("title", data.get("alertTitle", "OK")),
            description=data.get(
                "desc", data.get("description", data.get("alertDescription", ""))
            ),
        )


# ---------------------------------------------------------------------------
# Modules (Microinverter panels)
# ---------------------------------------------------------------------------


@dataclass
class Module:
    """A single microinverter module (panel-level data)."""

    plc_sn: str
    addr: int
    last_update: str
    last_update_time: int
    now: float
    today_power: float
    total_power: float
    now_unit: str
    today_power_unit: str
    total_power_unit: str
    version: str
    status: str
    page: int
    model: int
    model_name: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Module:
        return cls(
            plc_sn=data.get("plcSN", ""),
            addr=data.get("addr", 0),
            last_update=data.get("lastUpdate", ""),
            last_update_time=data.get("lastUpdateTime", 0),
            now=data.get("now", 0),
            today_power=data.get("todayPower", 0),
            total_power=data.get("totalPower", 0),
            now_unit=data.get("nowUnit", "W"),
            today_power_unit=data.get("todayPowerUnit", "kWh"),
            total_power_unit=data.get("totalPowerUnit", "kWh"),
            version=data.get("version", ""),
            status=data.get("status", "0000"),
            page=data.get("page", 0),
            model=data.get("model", 0),
            model_name=data.get("model_name", "-"),
        )


@dataclass
class DeviceModules:
    """Modules grouped by gateway/device serial number."""

    sn: str
    is_phase: bool
    modules: list[Module]
    status: int
    status_title: str
    alert_code: str
    alert_title: str
    model: int
    model_name: str
    last_update: str
    version: str
    alias: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeviceModules:
        return cls(
            sn=data.get("sn", ""),
            is_phase=data.get("isPhase", False),
            modules=[Module.from_dict(m) for m in data.get("modules", [])],
            status=data.get("status", -1),
            status_title=data.get("statusTitle", "offline"),
            alert_code=data.get("alertCode", ""),
            alert_title=data.get("alertTitle", ""),
            model=data.get("model", 0),
            model_name=data.get("modelName", ""),
            last_update=data.get("lastUpdate", ""),
            version=data.get("version", ""),
            alias=data.get("alias", ""),
        )


@dataclass
class SiteModulesData:
    """All modules for a site, grouped by device."""

    devices: list[DeviceModules]
    total_plc: int
    is_all: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SiteModulesData:
        return cls(
            devices=[DeviceModules.from_dict(d) for d in data.get("list", [])],
            total_plc=data.get("total_plc", 0),
            is_all=data.get("is_all", True),
        )


# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------


@dataclass
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
    def from_dict(cls, data: dict[str, Any]) -> Device:
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


@dataclass
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
    def from_dict(cls, data: dict[str, Any]) -> DeviceDetail:
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


@dataclass
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
    def from_dict(cls, data: dict[str, Any]) -> DeviceStatisticsOverview:
        return cls(
            max_now=data.get("maxNow", 0),
            total_now=data.get("totalNow", 0),
            total_now_unit=data.get("totalNowUnit", "W"),
            currency_unit=data.get("currency_unit", ""),
            local_electric_price=data.get("local_electric_price", 0),
            production=ProductionStatistics.from_dict(data.get("production", {})),
            environmental_benefit=EnvironmentalBenefit.from_dict(
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
            energy=EnergyFlow.from_dict(data.get("energy", {})),
        )


@dataclass
class PowerParameter:
    """A power parameter available for a device."""

    name: str
    unit: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PowerParameter:
        return cls(name=data["name"], unit=data["unit"])


# ---------------------------------------------------------------------------
# Site
# ---------------------------------------------------------------------------


@dataclass
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
    def from_dict(cls, data: dict[str, Any]) -> SiteDeviceSummary:
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


@dataclass
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
    def from_dict(cls, data: dict[str, Any]) -> Site:
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
            devices=[SiteDeviceSummary.from_dict(d) for d in data.get("sn", [])],
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


@dataclass
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
    def from_dict(cls, data: dict[str, Any]) -> SiteDetail:
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


@dataclass
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
    def from_dict(cls, data: dict[str, Any]) -> DeviceOverviewItem:
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


@dataclass
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
    def from_dict(cls, data: dict[str, Any]) -> SiteOverview:
        return cls(
            production=ProductionStatistics.from_dict(
                data.get("statisticsProduction", {})
            ),
            benefit=EnvironmentalBenefit.from_dict(data.get("benefit", {})),
            status=data.get("status", -1),
            status_title=data.get("statusTitle", "offline"),
            last_update_cal=data.get("lastUpdateCal", ""),
            last_update=data.get("lastUpdate", ""),
            created_at=data.get("createdAt", ""),
            device_list=[
                DeviceOverviewItem.from_dict(d) for d in data.get("deviceList", [])
            ],
            energy=EnergyFlow.from_dict(data.get("energy", {})),
            alert=AlertInfo.from_dict(data.get("alert", {})),
            max_power=data.get("max_power", 0),
            components=data.get("components", []),
        )


# ---------------------------------------------------------------------------
# Charts / Statistics
# ---------------------------------------------------------------------------


@dataclass
class ChartSeries:
    """A single data series in a chart."""

    name: str
    data: list[float | None]
    stack: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChartSeries:
        return cls(
            name=data.get("name", ""),
            data=data.get("data", []),
            stack=data.get("stack", ""),
        )


@dataclass
class ChartData:
    """Chart data from statistics/echarts endpoints."""

    legend: list[str]
    x_axis_data: list[str]
    series: list[ChartSeries]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChartData:
        return cls(
            legend=data.get("legend", []),
            x_axis_data=data.get("xAxisData", []),
            series=[ChartSeries.from_dict(s) for s in data.get("series", [])],
        )


@dataclass
class DateStatistics:
    """Statistics for a specific date period."""

    power: str
    consumption: str
    economic: str
    power_unit: str
    consumption_unit: str
    economic_unit: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DateStatistics:
        return cls(
            power=data.get("power", "0"),
            consumption=data.get("consumption", "0"),
            economic=data.get("economic", "0"),
            power_unit=data.get("powerUnit", "kWh"),
            consumption_unit=data.get("consumptionUnit", "kWh"),
            economic_unit=data.get("economicUnit", ""),
        )


# ---------------------------------------------------------------------------
# Playback
# ---------------------------------------------------------------------------


@dataclass
class PlaybackModule:
    """Per-module playback data (5-min interval power values)."""

    plc_sn: str
    addr: int
    data: list[int]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlaybackModule:
        return cls(
            plc_sn=data.get("plcSN", ""),
            addr=data.get("addr", 0),
            data=data.get("data", []),
        )


@dataclass
class PlaybackData:
    """Device playback data including total power and per-module breakdown."""

    overview: ChartData
    modules: list[PlaybackModule]
    unit: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlaybackData:
        return cls(
            overview=ChartData.from_dict(data.get("overview", {})),
            modules=[PlaybackModule.from_dict(m) for m in data.get("modules", [])],
            unit=data.get("unit", ""),
        )


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------


@dataclass
class WeatherDay:
    """Weather data for a single day."""

    datetime: str
    temp: float
    temp_max: float
    temp_min: float
    icon: str
    week: str
    conditions: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WeatherDay:
        return cls(
            datetime=data.get("datetime", ""),
            temp=data.get("temp", 0),
            temp_max=data.get("tempMax", 0),
            temp_min=data.get("tempMin", 0),
            icon=data.get("icon", ""),
            week=data.get("week", ""),
            conditions=data.get("conditions", ""),
        )


@dataclass
class Weather:
    """7-day weather forecast for a site."""

    days: int
    temperature_unit: str
    forecasts: list[WeatherDay]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Weather:
        return cls(
            days=data.get("days", 7),
            temperature_unit=data.get("temperatureUnit", "Celsius"),
            forecasts=[WeatherDay.from_dict(d) for d in data.get("list", [])],
        )


# ---------------------------------------------------------------------------
# Global Overview
# ---------------------------------------------------------------------------


@dataclass
class OverviewData:
    """Global overview (all sites) from /overview/overview."""

    production: ProductionStatistics
    benefit: EnvironmentalBenefit
    site_count: int
    device_count: int
    mr_count: int
    gateway_count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OverviewData:
        return cls(
            production=ProductionStatistics.from_dict(
                data.get("statisticsProduction", {})
            ),
            benefit=EnvironmentalBenefit.from_dict(data.get("benefit", {})),
            site_count=data.get("siteCount", 0),
            device_count=data.get("deviceCount", 0),
            mr_count=data.get("mrCount", 0),
            gateway_count=data.get("gatewayCount", 0),
        )


@dataclass
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
    def from_dict(cls, data: dict[str, Any]) -> SiteStatusCounts:
        return cls(
            site_count=data.get("siteCount", 0),
            status_map=data.get("statusMap", {}),
        )


# ---------------------------------------------------------------------------
# Product / SN Info (Android-only)
# ---------------------------------------------------------------------------


@dataclass
class ProductFunction:
    """A capability/function supported by a product (e.g. parameter settings, network config)."""

    func_id: int
    func_name: str
    signal_mqtt: bool
    signal_bluetooth: bool
    signal_at: bool
    signal_ap: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProductFunction:
        return cls(
            func_id=data.get("func_id", 0),
            func_name=data.get("func_name", ""),
            signal_mqtt=data.get("signal_mqtt", False),
            signal_bluetooth=data.get("signal_bluetooth", False),
            signal_at=data.get("signal_at", False),
            signal_ap=data.get("signal_ap", False),
        )


@dataclass
class ProductInfo:
    """Product information for a device serial number."""

    sn: str
    model: int
    model_name: str
    functions: list[ProductFunction]
    is_exist: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProductInfo:
        return cls(
            sn=data.get("sn", ""),
            model=data.get("model", 0),
            model_name=data.get("modelName", ""),
            functions=[
                ProductFunction.from_dict(f) for f in data.get("funcList", [])
            ],
            is_exist=data.get("is_exist", False),
        )


# ---------------------------------------------------------------------------
# Device WiFi OTA (Android-only)
# ---------------------------------------------------------------------------


@dataclass
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
    def from_dict(cls, data: dict[str, Any]) -> DeviceWifiOta:
        return cls(
            sn=data.get("sn", ""),
            wifi_version=data.get("wifiVersion", ""),
            advice=data.get("advice", 2),
            address=data.get("address", ""),
        )


# ---------------------------------------------------------------------------
# Site Layout Info
# ---------------------------------------------------------------------------


@dataclass
class SiteLayout:
    """Site layout picture and scale information."""

    sid: str
    site_name: str
    layout_pic: str
    layout_scale: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SiteLayout:
        return cls(
            sid=data.get("sid", ""),
            site_name=data.get("siteName", ""),
            layout_pic=data.get("layoutPic", ""),
            layout_scale=data.get("layoutScale", 0),
        )