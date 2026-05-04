"""Edge — the "relationship" subtree of EDM.

An ``Edge`` is an edge between two :class:`Node` instances: a line between
two buses, an interconnector between two bidding zones, a pipe between two
delivery points. Edges sit sibling to ``Node`` under :class:`Element`, not
under ``Node`` — this keeps ``members`` and ``tz`` off Edges, where they
don't apply.

Concrete edge-equipment subclasses (Line, Link, Pipe, Interconnection)
live in :mod:`energydatamodel.grid` under :class:`EdgeAsset`. Note that
``Transformer`` is a node (``NodeAsset``), not an edge — it has HV and
LV sides that lines connect to.
"""

from __future__ import annotations

from dataclasses import dataclass

from energydatamodel.element import Element, infra
from energydatamodel.reference import Reference


@dataclass(repr=False, kw_only=True)
class Edge(Element):
    """An edge between two Nodes.

    Edges are **always directed by convention** — flow in the opposite
    direction is expressed as a signed value on the timeseries. The
    ``directed`` flag is kept for explicit cases (e.g. pure bidirectional
    pipes).

    A bare :class:`Element` passed as ``from_element`` / ``to_element`` is
    auto-wrapped in a :class:`Reference` at construction.
    """

    from_element: Reference | None = infra(default=None)
    to_element: Reference | None = infra(default=None)
    directed: bool = infra(default=True)

    def __post_init__(self, lat=None, lon=None) -> None:
        super().__post_init__(lat, lon)
        if isinstance(self.from_element, Element):
            self.from_element = Reference(self.from_element)
        if isinstance(self.to_element, Element):
            self.to_element = Reference(self.to_element)
