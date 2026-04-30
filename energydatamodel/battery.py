"""Battery asset."""

from dataclasses import dataclass

from energydatamodel.bases import NodeAsset

__all__ = ["Battery"]


@dataclass(repr=False, kw_only=True)
class Battery(NodeAsset):
    storage_capacity: float | None = None
    min_soc: float | None = None
    max_charge: float | None = None
    max_discharge: float | None = None
    charge_efficiency: float | None = None
    discharge_efficiency: float | None = None
