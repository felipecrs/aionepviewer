"""Global overview model for the NEP API."""

from __future__ import annotations

from typing import Any

from .energy import EnvironmentalBenefit, ProductionStatistics


class OverviewData:
    """Global overview (all sites) from /overview/overview."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def production(self) -> ProductionStatistics:
        return ProductionStatistics(self.raw_data.get("statisticsProduction", {}))

    @property
    def benefit(self) -> EnvironmentalBenefit:
        return EnvironmentalBenefit(self.raw_data.get("benefit", {}))

    @property
    def site_count(self) -> int:
        return self.raw_data.get("siteCount", 0)

    @property
    def device_count(self) -> int:
        return self.raw_data.get("deviceCount", 0)

    @property
    def mr_count(self) -> int:
        return self.raw_data.get("mrCount", 0)

    @property
    def gateway_count(self) -> int:
        return self.raw_data.get("gatewayCount", 0)