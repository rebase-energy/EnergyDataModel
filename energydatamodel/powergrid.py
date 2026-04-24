"""Power-grid concrete classes.

* :class:`EdgeAsset` is the single ``(Edge, Asset)`` mixin point on the edge
  side. Concrete edge-equipment classes (``Line``, ``Link``, ``Transformer``,
  ``Pipe``, ``Interconnection``) single-inherit from here.
* GridNode subclasses (``JunctionPoint``, ``Meter``, ``DeliveryPoint``) live
  here as concrete topological points. The ``GridNode`` base lives in
  :mod:`energydatamodel.bases`.
* ``SubNetwork`` and ``Network`` are :class:`Collection` subclasses used to
  group buses + lines.
* ``Carrier`` is a plain value type (not an Element).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from energydatamodel.asset import Asset
from energydatamodel.bases import GridNode
from energydatamodel.containers import Collection
from energydatamodel.edge import Edge


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
    (``Line``, ``Link``, ``Transformer``, ``Pipe``, ``Interconnection``)
    single-inherit from here.
    """

    _BASE_FIELDS: ClassVar[frozenset] = Edge._BASE_FIELDS | Asset._BASE_FIELDS


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
class Transformer(EdgeAsset):
    """Transformer between two buses."""

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
