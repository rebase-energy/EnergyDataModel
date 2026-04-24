"""Hydro assets."""

from dataclasses import dataclass

import pandas as pd

from energydatamodel.bases import NodeAsset


@dataclass(repr=False, kw_only=True)
class Reservoir(NodeAsset):
    """Reservoir used in a hydroelectric power plant for storing water."""

    capacity: float | None = None  #: Water capacity in cubic meters.
    surface_area: float | None = None  #: Surface area in square kilometers.
    average_depth: float | None = None  #: Average depth in meters.


@dataclass(repr=False, kw_only=True)
class HydroTurbine(NodeAsset):
    """Individual hydro turbine in a hydroelectric plant."""

    turbine_type: str | None = None  #: e.g. Francis, Kaplan.
    capacity: float | None = None  #: Max power output in MW.
    efficiency: float | None = None  #: Efficiency percentage.


@dataclass(repr=False, kw_only=True)
class HydroPowerPlant(NodeAsset):
    """Hydro power plant."""

    capacity: float | None = None  #: in MW.
    river: str | None = None
    annual_output: float | None = None  #: annual energy output in MWh.
    turbine_type: str | None = None
    reservoir_capacity: float | None = None
    environmental_impact: str | None = None
    maintenance_schedule: pd.DataFrame | dict | None = None
