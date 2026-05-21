"""Product information models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ProductFunction:
    """A capability/function supported by a product."""

    func_id: int
    func_name: str
    signal_mqtt: bool
    signal_bluetooth: bool
    signal_at: bool
    signal_ap: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ProductFunction:
        return cls(
            func_id=data.get("func_id", 0),
            func_name=data.get("func_name", ""),
            signal_mqtt=data.get("signal_mqtt", False),
            signal_bluetooth=data.get("signal_bluetooth", False),
            signal_at=data.get("signal_at", False),
            signal_ap=data.get("signal_ap", False),
        )


@dataclass(slots=True)
class ProductInfo:
    """Product information for a device serial number."""

    sn: str
    model: int
    model_name: str
    functions: list[ProductFunction]
    is_exist: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ProductInfo:
        return cls(
            sn=data.get("sn", ""),
            model=data.get("model", 0),
            model_name=data.get("modelName", ""),
            functions=[
                ProductFunction.from_api(f) for f in data.get("funcList", [])
            ],
            is_exist=data.get("is_exist", False),
        )