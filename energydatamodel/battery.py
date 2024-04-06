from dataclasses import dataclass
import typing as t

import energydatamodel as edm


@dataclass(repr=False)
class Battery(edm.EnergyAsset):
    storage_capacity: t.Optional[float] = None
    min_soc: t.Optional[float] = None
    max_charge: t.Optional[float] = None
    max_discharge: t.Optional[float] = None
    charge_efficiency: t.Optional[float] = None
    discharge_efficiency: t.Optional[float] = None