"""Power-grid concrete classes.

* :class:`EdgeAsset` is the single ``(Edge, Asset)`` mixin point on the edge
  side. Concrete edge-equipment classes (``Line``, ``Link``, ``Pipe``,
  ``Interconnection``) single-inherit from here.
* GridNode subclasses (``JunctionPoint``, ``Meter``, ``DeliveryPoint``) live
  here as concrete topological points. The ``GridNode`` base lives in
  :mod:`energydatamodel.bases`. ``Transformer`` is also a :class:`GridNode`
  (a vertex with HV and LV sides on the electricity carrier).
* ``SubNetwork`` and ``Network`` are :class:`Collection` subclasses used to
  group buses + lines.
* ``Carrier`` is a plain value type (not an Element).
"""

from dataclasses import dataclass

from energydatamodel.asset import Asset
from energydatamodel.bases import GridNode
from energydatamodel.containers import Collection
from energydatamodel.edge import Edge

__all__ = [
    "Carrier",
    "EdgeAsset",
    "JunctionPoint",
    "Meter",
    "DeliveryPoint",
    "Transformer",
    "Line",
    "Link",
    "Pipe",
    "Interconnection",
    "SubNetwork",
    "Network",
]


@dataclass
class Carrier:
    """Energy carrier (electricity, gas, ...). Plain value type."""

    name: str
    type: str


# ----------------------------------------------------------------- EdgeAsset


@dataclass(repr=False, kw_only=True)
class EdgeAsset(Edge, Asset):
    """Mixin intermediate: an ``Edge`` that is also an ``Asset``.

    Single mixin point on the edge side. Concrete edge equipment classes
    (``Line``, ``Link``, ``Pipe``, ``Interconnection``) single-inherit from here.
    """


# --------------------------------------------------------------------- Nodes


@dataclass(repr=False, kw_only=True)
class JunctionPoint(GridNode):
    """A bus / junction in an electrical network."""


@dataclass(repr=False, kw_only=True)
class Meter(GridNode):
    """A metering point."""


@dataclass(repr=False, kw_only=True)
class DeliveryPoint(GridNode):
    """A delivery point (end of a feeder)."""


@dataclass(repr=False, kw_only=True)
class Transformer(GridNode):
    """Transformer joining HV and LV sides of an electrical network.

    Modeled as a topological grid node, not an edge — matches pandapower /
    PyPSA topology where a transformer is a vertex with two voltage sides
    and edges (Lines) attach to each side. Inherits ``carrier`` from
    :class:`GridNode` (always electricity for a transformer).
    """

    capacity: float | None = None  #: Apparent-power rating in MVA.
    voltage_hv: float | None = None  #: HV-side nominal voltage in kV.
    voltage_lv: float | None = None  #: LV-side nominal voltage in kV.


# ----------------------------------------------------------------- Edges


@dataclass(repr=False, kw_only=True)
class Line(EdgeAsset):
    """Transmission or distribution line."""

    capacity: float | None = None


@dataclass(repr=False, kw_only=True)
class Link(EdgeAsset):
    """DC link or similar two-node power link."""

    capacity: float | None = None


@dataclass(repr=False, kw_only=True)
class Interconnection(EdgeAsset):
    """Cross-border / cross-area interconnection between two ``Area`` nodes.

    The only Edge that carries paired forward/backward capacities —
    TSO data typically reports them separately.
    """

    capacity_forward: float | None = None
    capacity_backward: float | None = None


@dataclass(repr=False, kw_only=True)
class Pipe(EdgeAsset):
    """Gas / heat pipe."""

    capacity: float | None = None
    medium: str = "gas"


# ----------------------------------------------------------------- Collections


@dataclass(repr=False, kw_only=True)
class SubNetwork(Collection):
    """Subnetwork grouping buses + lines."""


@dataclass(repr=False, kw_only=True)
class Network(Collection):
    """Network grouping subnetworks + transformers + links."""
