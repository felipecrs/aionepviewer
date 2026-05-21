"""aionepviewer - Async Python library for the NEP solar inverter cloud API."""

from .auth import NepAuth
from .const import DEFAULT_HOST
from .exceptions import (
    NepApiError,
    NepAuthError,
    NepConnectionError,
    NepError,
    NepTimeoutError,
)
from .models.alert import AlertInfo, DeviceStatus
from .models.auth import AccountInfo, AuthData, TokenInfo, UserInfo
from .models.chart import ChartData, ChartSeries, ChartType, DateStatistics, DateStatisticsType
from .models.device import (
    Device,
    DeviceDetail,
    DeviceOverviewItem,
    DeviceStatisticsOverview,
    DeviceWifiOta,
    PowerParameter,
)
from .models.energy import EnergyFlow, EnergySource, EnvironmentalBenefit, ProductionStatistics
from .models.module import DeviceModules, Module, SiteModulesData
from .models.overview import OverviewData
from .models.playback import PlaybackData, PlaybackModule, PlaybackType
from .models.product import ProductFunction, ProductInfo
from .models.report import ReportSettings
from .models.site import Site, SiteDetail, SiteDeviceSummary, SiteLayout, SiteOverview, SiteStatusCounts
from .models.weather import Weather, WeatherDay
from .nepviewer import NepViewer

__all__ = [
    # Client
    "NepViewer",
    "NepAuth",
    # Constants
    "DEFAULT_HOST",
    # Exceptions
    "NepError",
    "NepAuthError",
    "NepConnectionError",
    "NepApiError",
    "NepTimeoutError",
    # Enums
    "ChartType",
    "DateStatisticsType",
    "DeviceStatus",
    "PlaybackType",
    # Auth models
    "AuthData",
    "UserInfo",
    "TokenInfo",
    "AccountInfo",
    # Energy
    "EnergyFlow",
    "EnergySource",
    "ProductionStatistics",
    "EnvironmentalBenefit",
    # Alert
    "AlertInfo",
    # Device models
    "Device",
    "DeviceDetail",
    "DeviceStatisticsOverview",
    "DeviceOverviewItem",
    "DeviceModules",
    "DeviceWifiOta",
    "PowerParameter",
    # Product models
    "ProductFunction",
    "ProductInfo",
    # Module models
    "Module",
    "SiteModulesData",
    # Site models
    "Site",
    "SiteDetail",
    "SiteOverview",
    "SiteDeviceSummary",
    "SiteLayout",
    "SiteStatusCounts",
    # Chart models
    "ChartData",
    "ChartSeries",
    "DateStatistics",
    # Playback
    "PlaybackData",
    "PlaybackModule",
    # Weather
    "Weather",
    "WeatherDay",
    # Overview
    "OverviewData",
    # Report
    "ReportSettings",
]