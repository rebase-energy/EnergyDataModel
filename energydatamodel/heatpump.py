"""Heat pump asset."""

from dataclasses import dataclass

from energydatamodel.bases import NodeAsset

__all__ = ["HeatPump"]


@dataclass(repr=False, kw_only=True)
class HeatPump(NodeAsset):
    """A heat pump in an energy system."""

    capacity: float | None = None  #: heating/cooling capacity in kW.
    cop: float | None = None  #: coefficient of performance.
    energy_source: str | None = None  #: e.g. 'electricity', 'geothermal'.
