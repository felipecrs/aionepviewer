"""Report settings model for the NEP API."""

from __future__ import annotations

from typing import Any


class ReportSettings:
    """Email report notification settings for a device."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sn(self) -> str:
        return self.raw_data.get("sn", "")

    @property
    def daily(self) -> bool:
        return self.raw_data.get("optionsDaily", False)

    @property
    def weekly(self) -> bool:
        return self.raw_data.get("optionsWeekly", False)

    @property
    def monthly(self) -> bool:
        return self.raw_data.get("optionsMonthly", False)

    @property
    def alert_hourly(self) -> bool:
        return self.raw_data.get("alertHourly", False)

    @property
    def alert_time(self) -> bool:
        return self.raw_data.get("alertTime", False)

    @property
    def alert_start(self) -> str:
        return self.raw_data.get("alertStart", "8")

    @property
    def alert_end(self) -> str:
        return self.raw_data.get("alertEnd", "17")