"""Convenience constructors that build ``TimeSeriesDescriptor`` instances with
pre-filled metric strings for common energy quantities.

Each constructor returns a fresh ``TimeSeriesDescriptor`` (the underlying
dataclass is frozen, so we always instantiate anew).
"""

from __future__ import annotations

from timedatamodel import DataType, Frequency, TimeSeriesDescriptor

from energydatamodel.quantities import Kind, Quantity, Scope, build_metric


def _make(
    quantity: Quantity,
    kind: Kind,
    scope: Scope,
    unit: str,
    data_type: DataType | None,
    frequency: Frequency | None,
    timezone: str,
    description: str | None,
) -> TimeSeriesDescriptor:
    return TimeSeriesDescriptor(
        name=build_metric(quantity, kind, scope),
        unit=unit,
        data_type=data_type,
        frequency=frequency,
        timezone=timezone,
        description=description,
    )


# ---------------------------------------------------------------------
# Electricity
# ---------------------------------------------------------------------


def electricity_supply(
    unit: str = "MW",
    data_type: DataType | None = DataType.ACTUAL,
    frequency: Frequency | None = None,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    return _make(Quantity.ELECTRICITY, Kind.SUPPLY, Scope.POINT, unit, data_type, frequency, timezone, description)


def electricity_demand(
    unit: str = "MW",
    data_type: DataType | None = DataType.ACTUAL,
    frequency: Frequency | None = None,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    return _make(Quantity.ELECTRICITY, Kind.DEMAND, Scope.POINT, unit, data_type, frequency, timezone, description)


def electricity_supply_area(
    unit: str = "MW",
    data_type: DataType | None = DataType.ACTUAL,
    frequency: Frequency | None = None,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    return _make(Quantity.ELECTRICITY, Kind.SUPPLY, Scope.AREA, unit, data_type, frequency, timezone, description)


def electricity_demand_area(
    unit: str = "MW",
    data_type: DataType | None = DataType.ACTUAL,
    frequency: Frequency | None = None,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    return _make(Quantity.ELECTRICITY, Kind.DEMAND, Scope.AREA, unit, data_type, frequency, timezone, description)


# ---------------------------------------------------------------------
# Prices & flows
# ---------------------------------------------------------------------


def spot_price(
    unit: str = "EUR / MWh",
    data_type: DataType | None = DataType.ACTUAL,
    frequency: Frequency | None = None,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    return _make(Quantity.PRICE, Kind.SPOT, Scope.POINT, unit, data_type, frequency, timezone, description)


def cross_border_flow(
    unit: str = "MW",
    data_type: DataType | None = DataType.ACTUAL,
    frequency: Frequency | None = None,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    return _make(Quantity.ELECTRICITY, Kind.FLOW, Scope.AREA, unit, data_type, frequency, timezone, description)


# ---------------------------------------------------------------------
# Weather & other quantities
# ---------------------------------------------------------------------


def temperature(
    unit: str = "degC",
    data_type: DataType | None = DataType.ACTUAL,
    frequency: Frequency | None = None,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    return _make(Quantity.TEMPERATURE, Kind.STATE, Scope.POINT, unit, data_type, frequency, timezone, description)


def gas_supply(
    unit: str = "MW",
    data_type: DataType | None = DataType.ACTUAL,
    frequency: Frequency | None = None,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    return _make(Quantity.GAS, Kind.SUPPLY, Scope.POINT, unit, data_type, frequency, timezone, description)


def gas_demand(
    unit: str = "MW",
    data_type: DataType | None = DataType.ACTUAL,
    frequency: Frequency | None = None,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    return _make(Quantity.GAS, Kind.DEMAND, Scope.POINT, unit, data_type, frequency, timezone, description)


def heating_demand(
    unit: str = "MW",
    data_type: DataType | None = DataType.ACTUAL,
    frequency: Frequency | None = None,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    return _make(Quantity.HEATING, Kind.DEMAND, Scope.POINT, unit, data_type, frequency, timezone, description)


# ---------------------------------------------------------------------
# Grid state
# ---------------------------------------------------------------------


def grid_frequency(
    unit: str = "Hz",
    data_type: DataType | None = DataType.OBSERVATION,
    frequency: Frequency | None = Frequency.PT1S,
    timezone: str = "UTC",
    description: str | None = None,
) -> TimeSeriesDescriptor:
    """Grid frequency (Hz) — a per-synchronous-area observation.

    Frequency is shared across all zones in an AC-synchronous grid (NSA, CESA,
    GBSA, ISA, BSA, IPSA), so this constructor uses :data:`Scope.AREA`. Default
    sample interval is one second; nominal value (50 / 60 Hz) lives on the
    :class:`SynchronousArea` itself, not on the descriptor.
    """
    return _make(
        Quantity.FREQUENCY, Kind.STATE, Scope.AREA,
        unit, data_type, frequency, timezone, description,
    )
