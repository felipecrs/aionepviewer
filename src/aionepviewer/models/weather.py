"""Weather models for the NEP API."""

from __future__ import annotations

from typing import Any


class WeatherDay:
    """Weather data for a single day."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def datetime(self) -> str:
        return self.raw_data.get("datetime", "")

    @property
    def temp(self) -> float:
        return self.raw_data.get("temp", 0)

    @property
    def temp_max(self) -> float:
        return self.raw_data.get("tempMax", 0)

    @property
    def temp_min(self) -> float:
        return self.raw_data.get("tempMin", 0)

    @property
    def icon(self) -> str:
        return self.raw_data.get("icon", "")

    @property
    def week(self) -> str:
        return self.raw_data.get("week", "")

    @property
    def conditions(self) -> str:
        return self.raw_data.get("conditions", "")


class Weather:
    """7-day weather forecast for a site."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def days(self) -> int:
        return self.raw_data.get("days", 7)

    @property
    def temperature_unit(self) -> str:
        return self.raw_data.get("temperatureUnit", "Celsius")

    @property
    def forecasts(self) -> list[WeatherDay]:
        return [WeatherDay(d) for d in self.raw_data.get("list", [])]