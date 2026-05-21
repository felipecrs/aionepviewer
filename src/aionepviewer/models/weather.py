"""Weather models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
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
    def from_api(cls, data: dict[str, Any]) -> WeatherDay:
        return cls(
            datetime=data.get("datetime", ""),
            temp=data.get("temp", 0),
            temp_max=data.get("tempMax", 0),
            temp_min=data.get("tempMin", 0),
            icon=data.get("icon", ""),
            week=data.get("week", ""),
            conditions=data.get("conditions", ""),
        )


@dataclass(slots=True)
class Weather:
    """7-day weather forecast for a site."""

    days: int
    temperature_unit: str
    forecasts: list[WeatherDay]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Weather:
        return cls(
            days=data.get("days", 7),
            temperature_unit=data.get("temperatureUnit", "Celsius"),
            forecasts=[WeatherDay.from_api(d) for d in data.get("list", [])],
        )