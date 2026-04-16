"""Heat pump asset."""

from dataclasses import dataclass
from typing import Optional

from energydatamodel.bases import Asset


@dataclass(repr=False, kw_only=True)
class HeatPump(Asset):
    """A heat pump in an energy system."""

    capacity: Optional[float] = None  #: heating/cooling capacity in kW.
    cop: Optional[float] = None  #: coefficient of performance.
    energy_source: Optional[str] = None  #: e.g. 'electricity', 'geothermal'.
