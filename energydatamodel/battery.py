"""Battery asset."""

from dataclasses import dataclass
from typing import Optional

from energydatamodel.bases import Asset


@dataclass(repr=False, kw_only=True)
class Battery(Asset):
    storage_capacity: Optional[float] = None
    min_soc: Optional[float] = None
    max_charge: Optional[float] = None
    max_discharge: Optional[float] = None
    charge_efficiency: Optional[float] = None
    discharge_efficiency: Optional[float] = None
