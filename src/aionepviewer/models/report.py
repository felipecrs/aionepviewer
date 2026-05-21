"""Report settings model for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ReportSettings:
    """Email report notification settings for a device."""

    sn: str
    daily: bool
    weekly: bool
    monthly: bool
    alert_hourly: bool
    alert_time: bool
    alert_start: str
    alert_end: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ReportSettings:
        return cls(
            sn=data.get("sn", ""),
            daily=data.get("optionsDaily", False),
            weekly=data.get("optionsWeekly", False),
            monthly=data.get("optionsMonthly", False),
            alert_hourly=data.get("alertHourly", False),
            alert_time=data.get("alertTime", False),
            alert_start=data.get("alertStart", "8"),
            alert_end=data.get("alertEnd", "17"),
        )