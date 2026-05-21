"""Chart and statistics models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(slots=True)
class ChartSeries:
    """A single data series in a chart."""

    name: str
    data: list[float | None]
    stack: str = ""

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChartSeries:
        return cls(
            name=data.get("name", ""),
            data=data.get("data", []),
            stack=data.get("stack", ""),
        )


@dataclass(slots=True)
class ChartData:
    """Chart data from statistics/echarts endpoints."""

    legend: list[str]
    x_axis_data: list[str]
    series: list[ChartSeries]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChartData:
        return cls(
            legend=data.get("legend", []),
            x_axis_data=data.get("xAxisData", []),
            series=[ChartSeries.from_api(s) for s in data.get("series", [])],
        )


@dataclass(slots=True)
class DateStatistics:
    """Statistics for a specific date period."""

    power: str
    consumption: str
    economic: str
    power_unit: str
    consumption_unit: str
    economic_unit: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DateStatistics:
        return cls(
            power=data.get("power", "0"),
            consumption=data.get("consumption", "0"),
            economic=data.get("economic", "0"),
            power_unit=data.get("powerUnit", "kWh"),
            consumption_unit=data.get("consumptionUnit", "kWh"),
            economic_unit=data.get("economicUnit", ""),
        )