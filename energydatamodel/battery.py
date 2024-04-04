from dataclasses import dataclass, field
import typing as t

from energydatamodel import EnergyAsset


@dataclass(repr=False)
class Battery(EnergyAsset):
    storage_capacity: t.Optional[float] = None
    min_soc: t.Optional[float] = None
    max_charge: t.Optional[float] = None
    max_discharge: t.Optional[float] = None
    charge_efficiency: t.Optional[float] = None
    discharge_efficiency: t.Optional[float] = None