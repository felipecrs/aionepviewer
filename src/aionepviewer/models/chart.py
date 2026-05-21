"""Chart and statistics models for the NEP API."""

from __future__ import annotations

from enum import IntEnum
from typing import Any


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


class ChartSeries:
    """A single data series in a chart."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def name(self) -> str:
        return self.raw_data.get("name", "")

    @property
    def data(self) -> list[float | None]:
        return self.raw_data.get("data", [])

    @property
    def stack(self) -> str:
        return self.raw_data.get("stack", "")


class ChartData:
    """Chart data from statistics/echarts endpoints."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def legend(self) -> list[str]:
        return self.raw_data.get("legend", [])

    @property
    def x_axis_data(self) -> list[str]:
        return self.raw_data.get("xAxisData", [])

    @property
    def series(self) -> list[ChartSeries]:
        return [ChartSeries(s) for s in self.raw_data.get("series", [])]


class DateStatistics:
    """Statistics for a specific date period."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def power(self) -> str:
        return self.raw_data.get("power", "0")

    @property
    def consumption(self) -> str:
        return self.raw_data.get("consumption", "0")

    @property
    def economic(self) -> str:
        return self.raw_data.get("economic", "0")

    @property
    def power_unit(self) -> str:
        return self.raw_data.get("powerUnit", "kWh")

    @property
    def consumption_unit(self) -> str:
        return self.raw_data.get("consumptionUnit", "kWh")

    @property
    def economic_unit(self) -> str:
        return self.raw_data.get("economicUnit", "")