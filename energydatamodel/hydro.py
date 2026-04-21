"""Hydro assets."""

from dataclasses import dataclass
from typing import Optional, Union

import pandas as pd

from energydatamodel.bases import NodeAsset


@dataclass(repr=False, kw_only=True)
class Reservoir(NodeAsset):
    """Reservoir used in a hydroelectric power plant for storing water."""

    capacity: Optional[float] = None  #: Water capacity in cubic meters.
    surface_area: Optional[float] = None  #: Surface area in square kilometers.
    average_depth: Optional[float] = None  #: Average depth in meters.


@dataclass(repr=False, kw_only=True)
class HydroTurbine(NodeAsset):
    """Individual hydro turbine in a hydroelectric plant."""

    turbine_type: Optional[str] = None  #: e.g. Francis, Kaplan.
    capacity: Optional[float] = None  #: Max power output in MW.
    efficiency: Optional[float] = None  #: Efficiency percentage.


@dataclass(repr=False, kw_only=True)
class HydroPowerPlant(NodeAsset):
    """Hydro power plant."""

    capacity: Optional[float] = None  #: in MW.
    river: Optional[str] = None
    annual_output: Optional[float] = None  #: annual energy output in MWh.
    turbine_type: Optional[str] = None
    reservoir_capacity: Optional[float] = None
    environmental_impact: Optional[str] = None
    maintenance_schedule: Optional[Union[pd.DataFrame, dict]] = None
