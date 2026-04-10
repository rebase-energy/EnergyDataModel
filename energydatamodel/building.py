"""Building and House — Assets that also contain other Assets via inherited members."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


from energydatamodel.bases import Asset


@dataclass(repr=False, kw_only=True)
class Building(Asset):
    """A building. An :class:`Asset` (location, capacity-like fields) that also
    contains child Entities via the inherited ``members`` list."""

    type: Optional[str] = None


@dataclass(repr=False, kw_only=True)
class House(Asset):
    """A house. Same structure as :class:`Building` with a few convenience
    accessors."""

    type: Optional[str] = None

    # ----- convenience queries -------------------------------------------------
    def has_demand(self) -> bool:
        return bool(self.timeseries)

    def has_pvsystem(self) -> bool:
        from energydatamodel.solar import PVSystem
        return any(isinstance(m, PVSystem) for m in self.members)

    def has_battery(self) -> bool:
        from energydatamodel.battery import Battery
        return any(isinstance(m, Battery) for m in self.members)

    def get_pvsystems(self) -> list:
        from energydatamodel.solar import PVSystem
        return [m for m in self.members if isinstance(m, PVSystem)]

    def get_batteries(self) -> list:
        from energydatamodel.battery import Battery
        return [m for m in self.members if isinstance(m, Battery)]
