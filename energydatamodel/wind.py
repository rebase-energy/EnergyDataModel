"""Wind assets."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from energydatamodel.bases import NodeAsset
from energydatamodel.element import Element

__all__ = ["WindTurbine", "WindFarm", "WindPowerArea"]


@dataclass(repr=False, kw_only=True)
class WindTurbine(NodeAsset):
    capacity: float | pd.DataFrame | None = None
    hub_height: float | None = None
    rotor_diameter: float | None = None
    turbine_model: str | None = None
    power_curve: pd.DataFrame | dict | None = None
    power_coefficient_curve: pd.DataFrame | dict | None = None


@dataclass(repr=False, kw_only=True)
class WindFarm(NodeAsset):
    """A wind farm — an Asset that contains :class:`WindTurbine` members.

    Stored in the inherited ``members`` list (no separate typed field).
    ``add_child`` enforces the type at runtime.
    """

    capacity: float | pd.DataFrame | None = None
    farm_efficiency: pd.DataFrame | None = None

    def add_child(self, obj: Element) -> None:
        if not isinstance(obj, WindTurbine):
            raise TypeError(f"WindFarm only accepts WindTurbine children, got {type(obj).__name__}")
        self.members.append(obj)


@dataclass(repr=False, kw_only=True)
class WindPowerArea(NodeAsset):
    """A wind-power-potential area (e.g. offshore zone).

    The area's polygon lives in the inherited ``geometry`` field. Constituent
    turbines or farms (if any) live in the inherited ``members`` list.
    """

    capacity: float | pd.DataFrame | None = None
    area: float | None = None
    farm_efficiency: pd.DataFrame | None = None
