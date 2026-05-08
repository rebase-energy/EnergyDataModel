"""Building and House — Assets that also contain other Assets via inherited members."""

from dataclasses import dataclass

from energydatamodel.bases import NodeAsset

__all__ = ["Building", "House"]


@dataclass(repr=False, kw_only=True)
class Building(NodeAsset):
    """A building. A physical asset that also contains child Elements via the
    inherited ``members`` list."""

    type: str | None = None


@dataclass(repr=False, kw_only=True)
class House(NodeAsset):
    """A house. Same structure as :class:`Building` with a few convenience
    accessors."""

    type: str | None = None

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
