"""Energy vocabulary — Quantity / Kind / Scope enums + ``build_metric()``.

Replaces the old ``ElectricityDemand(TimeSeries)`` subclass pattern: a
``TimeSeries`` carries a string ``name`` field whose value is a dotted
metric string built from ``(Quantity, Kind, Scope)`` via
:func:`build_metric`.
"""

from __future__ import annotations

from enum import StrEnum


class Quantity(StrEnum):
    ELECTRICITY = "electricity"
    HEATING = "heating"
    COOLING = "cooling"
    GAS = "gas"
    TEMPERATURE = "temperature"
    PRICE = "price"
    FREQUENCY = "frequency"  # grid frequency in Hz (per synchronous area)


class Kind(StrEnum):
    DEMAND = "demand"
    SUPPLY = "supply"
    BALANCE = "balance"
    STATE = "state"
    SPOT = "spot"
    FLOW = "flow"


class Scope(StrEnum):
    POINT = "point"
    AREA = "area"


def build_metric(
    quantity: Quantity,
    kind: Kind,
    scope: Scope = Scope.POINT,
    *extras: str,
) -> str:
    """Build a dotted metric string, e.g. ``electricity.demand`` / ``electricity.demand.area``."""
    parts = [quantity.value, kind.value]
    if scope == Scope.AREA:
        parts.append("area")
    parts.extend(extras)
    return ".".join(parts)
