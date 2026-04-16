"""Wind assets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

import pandas as pd

from energydatamodel.bases import Asset
from energydatamodel.entity import Entity


@dataclass(repr=False, kw_only=True)
class WindTurbine(Asset):
    capacity: Optional[Union[float, pd.DataFrame]] = None
    hub_height: Optional[float] = None
    rotor_diameter: Optional[float] = None
    turbine_model: Optional[str] = None
    power_curve: Optional[Union[pd.DataFrame, dict]] = None
    power_coefficient_curve: Optional[Union[pd.DataFrame, dict]] = None


@dataclass(repr=False, kw_only=True)
class WindFarm(Asset):
    """A wind farm — an Asset that contains :class:`WindTurbine` members.

    Stored in the inherited ``members`` list (no separate typed field).
    ``add_child`` enforces the type at runtime.
    """

    capacity: Optional[Union[float, pd.DataFrame]] = None
    farm_efficiency: Optional[pd.DataFrame] = None

    def add_child(self, obj: Entity) -> None:
        if not isinstance(obj, WindTurbine):
            raise TypeError(
                f"WindFarm only accepts WindTurbine children, got {type(obj).__name__}"
            )
        self.members.append(obj)


@dataclass(repr=False, kw_only=True)
class WindPowerArea(Asset):
    """A wind-power-potential area (e.g. offshore zone).

    The area's polygon lives in the inherited ``geometry`` field. Constituent
    turbines or farms (if any) live in the inherited ``members`` list.
    """

    capacity: Optional[Union[float, pd.DataFrame]] = None
    area: Optional[float] = None
    farm_efficiency: Optional[pd.DataFrame] = None
