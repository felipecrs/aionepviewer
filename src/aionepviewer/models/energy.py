"""Energy flow and production models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class EnergySource:
    """A single energy source in the energy flow diagram."""

    power: float
    power_unit: str
    direction: int
    show: bool
    rate: float
    show_power: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnergySource:
        return cls(
            power=data.get("power", 0),
            power_unit=data.get("powerUnit", "W"),
            direction=data.get("direction", 0),
            show=data.get("show", False),
            rate=data.get("rate", 0),
            show_power=data.get("showPower", False),
        )


@dataclass(slots=True)
class EnergyFlow:
    """Energy flow diagram data (PV -> home, grid, battery, gen)."""

    pv_panel: EnergySource
    home: EnergySource
    grid: EnergySource
    battery: EnergySource
    generator: EnergySource

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnergyFlow:
        return cls(
            pv_panel=EnergySource.from_api(data.get("PVPanel", {})),
            home=EnergySource.from_api(data.get("home", {})),
            grid=EnergySource.from_api(data.get("grid", {})),
            battery=EnergySource.from_api(data.get("battery", {})),
            generator=EnergySource.from_api(data.get("gen", {})),
        )


@dataclass(slots=True)
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
    def from_api(cls, data: dict[str, Any]) -> ProductionStatistics:
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


@dataclass(slots=True)
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
    def from_api(cls, data: dict[str, Any]) -> EnvironmentalBenefit:
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