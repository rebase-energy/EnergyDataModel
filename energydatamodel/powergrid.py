"""Power-grid concrete classes.

* GridNode subclasses (``JunctionPoint``, ``Meter``, ``DeliveryPoint``) live
  here as concrete topological points. The ``GridNode`` base itself lives in
  :mod:`energydatamodel.bases`.
* Edge subclasses (``Line``, ``Link``, ``Transformer``,
  ``Interconnection``, ``Pipe``) live here. The ``Edge`` base lives in
  :mod:`energydatamodel.edge`.
* ``SubNetwork`` and ``Network`` are :class:`Collection` subclasses used to
  group buses + lines.
* ``Carrier`` is a plain value type (not an Entity).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from energydatamodel.bases import GridNode
from energydatamodel.containers import Collection
from energydatamodel.edge import Edge


@dataclass
class Carrier:
    """Energy carrier (electricity, gas, ...). Plain value type."""

    name: str
    type: str


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
class Line(Edge):
    """Transmission or distribution line."""

    capacity: Optional[float] = None


@dataclass(repr=False, kw_only=True)
class Link(Edge):
    """DC link or similar two-node power link."""

    capacity: Optional[float] = None


@dataclass(repr=False, kw_only=True)
class Transformer(Edge):
    """Transformer between two buses."""

    capacity: Optional[float] = None


@dataclass(repr=False, kw_only=True)
class Interconnection(Edge):
    """Cross-border / cross-area interconnection between two ``Area`` nodes.

    The only Edge that carries paired forward/backward capacities —
    TSO data typically reports them separately.
    """

    capacity_forward: Optional[float] = None
    capacity_backward: Optional[float] = None


@dataclass(repr=False, kw_only=True)
class Pipe(Edge):
    """Gas / heat pipe."""

    capacity: Optional[float] = None
    medium: str = "gas"


# ----------------------------------------------------------------- Collections


@dataclass(repr=False, kw_only=True)
class SubNetwork(Collection):
    """Subnetwork grouping buses + lines."""


@dataclass(repr=False, kw_only=True)
class Network(Collection):
    """Network grouping subnetworks + transformers + links."""
