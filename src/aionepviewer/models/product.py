"""Product information models for the NEP API."""

from __future__ import annotations

from typing import Any


class ProductFunction:
    """A capability/function supported by a product."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def func_id(self) -> int:
        return self.raw_data.get("func_id", 0)

    @property
    def func_name(self) -> str:
        return self.raw_data.get("func_name", "")

    @property
    def signal_mqtt(self) -> bool:
        return self.raw_data.get("signal_mqtt", False)

    @property
    def signal_bluetooth(self) -> bool:
        return self.raw_data.get("signal_bluetooth", False)

    @property
    def signal_at(self) -> bool:
        return self.raw_data.get("signal_at", False)

    @property
    def signal_ap(self) -> bool:
        return self.raw_data.get("signal_ap", False)


class ProductInfo:
    """Product information for a device serial number."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sn(self) -> str:
        return self.raw_data.get("sn", "")

    @property
    def model(self) -> int:
        return self.raw_data.get("model", 0)

    @property
    def model_name(self) -> str:
        return self.raw_data.get("modelName", "")

    @property
    def functions(self) -> list[ProductFunction]:
        return [ProductFunction(f) for f in self.raw_data.get("funcList", [])]

    @property
    def is_exist(self) -> bool:
        return self.raw_data.get("is_exist", False)