from dataclasses import dataclass, field
import typing as t

from energydatamodel import EnergyAsset


@dataclass(repr=False)
class Battery(EnergyAsset):
    capacity_kwh: t.Optional[float] = None
    min_soc_kwh: t.Optional[float] = None
    max_charge_kw: t.Optional[float] = None
    max_discharge_kw: t.Optional[float] = None
    charge_efficiency: t.Optional[float] = None
    discharge_efficiency: t.Optional[float] = None