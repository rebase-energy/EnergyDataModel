"""Wind assets."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from energydatamodel.bases import NodeAsset

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

    Members are stored in the inherited ``members`` list. Real wind farms
    can also contain met masts, transformers and substations, so children
    aren't restricted to ``WindTurbine`` — any :class:`Element` is accepted.
    """

    capacity: float | pd.DataFrame | None = None
    farm_efficiency: pd.DataFrame | None = None


@dataclass(repr=False, kw_only=True)
class WindPowerArea(NodeAsset):
    """A wind-power-potential area (e.g. offshore zone).

    The area's polygon lives in the inherited ``geometry`` field. Constituent
    turbines or farms (if any) live in the inherited ``members`` list.
    """

    capacity: float | pd.DataFrame | None = None
    area: float | None = None
    farm_efficiency: pd.DataFrame | None = None
