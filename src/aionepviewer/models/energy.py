"""Energy flow and production models for the NEP API."""

from __future__ import annotations

from typing import Any


class EnergySource:
    """A single energy source in the energy flow diagram."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def power(self) -> float:
        return self.raw_data.get("power", 0)

    @property
    def power_unit(self) -> str:
        return self.raw_data.get("powerUnit", "W")

    @property
    def direction(self) -> int:
        return self.raw_data.get("direction", 0)

    @property
    def show(self) -> bool:
        return self.raw_data.get("show", False)

    @property
    def rate(self) -> float:
        return self.raw_data.get("rate", 0)

    @property
    def show_power(self) -> bool:
        return self.raw_data.get("showPower", False)


class EnergyFlow:
    """Energy flow diagram data (PV -> home, grid, battery, gen)."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def pv_panel(self) -> EnergySource:
        return EnergySource(self.raw_data.get("PVPanel", {}))

    @property
    def home(self) -> EnergySource:
        return EnergySource(self.raw_data.get("home", {}))

    @property
    def grid(self) -> EnergySource:
        return EnergySource(self.raw_data.get("grid", {}))

    @property
    def battery(self) -> EnergySource:
        return EnergySource(self.raw_data.get("battery", {}))

    @property
    def generator(self) -> EnergySource:
        return EnergySource(self.raw_data.get("gen", {}))


class ProductionStatistics:
    """Energy production statistics."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def today(self) -> str:
        return self.raw_data.get("today", "0")

    @property
    def today_unit(self) -> str:
        return self.raw_data.get("todayUnit", "kWh")

    @property
    def yesterday(self) -> str:
        return self.raw_data.get("yesterday", "0")

    @property
    def yesterday_unit(self) -> str:
        return self.raw_data.get("yesterdayUnit", "kWh")

    @property
    def month(self) -> str:
        return self.raw_data.get("month", "0")

    @property
    def month_unit(self) -> str:
        return self.raw_data.get("monthUnit", "kWh")

    @property
    def year(self) -> str:
        return self.raw_data.get("year", "0")

    @property
    def year_unit(self) -> str:
        return self.raw_data.get("yearUnit", "kWh")

    @property
    def total(self) -> str:
        return self.raw_data.get("total", "0")

    @property
    def total_unit(self) -> str:
        return self.raw_data.get("totalUnit", "kWh")

    @property
    def total_now(self) -> str:
        return self.raw_data.get("totalNow", "0")

    @property
    def total_now_unit(self) -> str:
        return self.raw_data.get("totalNowUnit", "W")

    @property
    def total_money(self) -> str:
        return self.raw_data.get("totalMoney", "0")

    @property
    def today_money(self) -> str:
        return self.raw_data.get("todayMoney", "0")

    @property
    def yesterday_money(self) -> str:
        return self.raw_data.get("yesterdayMoney", "0")

    @property
    def month_money(self) -> str:
        return self.raw_data.get("monthMoney", "0")

    @property
    def total_money_unit(self) -> str:
        return self.raw_data.get("totalMoneyUnit", "")


class EnvironmentalBenefit:
    """Environmental benefit metrics."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def co2(self) -> str:
        return self.raw_data.get("co2", "0")

    @property
    def co2_unit(self) -> str:
        return self.raw_data.get("co2Unit", "kg")

    @property
    def tree(self) -> str:
        return self.raw_data.get("tree", "0")

    @property
    def tree_unit(self) -> str:
        return self.raw_data.get("treeUnit", "Trees")

    @property
    def car(self) -> str:
        return self.raw_data.get("car", "0")

    @property
    def car_unit(self) -> str:
        return self.raw_data.get("carUnit", "km")

    @property
    def light(self) -> str:
        return self.raw_data.get("light", "0")

    @property
    def light_unit(self) -> str:
        return self.raw_data.get("lightUnit", "H")

    @property
    def oil(self) -> str:
        return self.raw_data.get("oil", "0")

    @property
    def oil_unit(self) -> str:
        return self.raw_data.get("oilUnit", "BBL")