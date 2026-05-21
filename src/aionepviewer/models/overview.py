"""Global overview model for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .energy import EnvironmentalBenefit, ProductionStatistics


@dataclass(slots=True)
class OverviewData:
    """Global overview (all sites) from /overview/overview."""

    production: ProductionStatistics
    benefit: EnvironmentalBenefit
    site_count: int
    device_count: int
    mr_count: int
    gateway_count: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> OverviewData:
        return cls(
            production=ProductionStatistics.from_api(
                data.get("statisticsProduction", {})
            ),
            benefit=EnvironmentalBenefit.from_api(data.get("benefit", {})),
            site_count=data.get("siteCount", 0),
            device_count=data.get("deviceCount", 0),
            mr_count=data.get("mrCount", 0),
            gateway_count=data.get("gatewayCount", 0),
        )