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

from dataclasses import dataclass
from uuid import UUID

from energydatamodel.element import Element, infra
from energydatamodel.reference import Reference


@dataclass(repr=False, kw_only=True)
class Edge(Element):
    """An edge between two Nodes.

    Edges are **always directed by convention** — flow in the opposite
    direction is expressed as a signed value on the timeseries. The
    ``directed`` flag is kept for explicit cases (e.g. pure bidirectional
    pipes).

    Endpoints accept an :class:`Element`, a :class:`UUID`, or a
    :class:`Reference`; ``__post_init__`` normalizes all of these to
    :class:`Reference`. The widened input type is a constructor convenience
    — once the edge is built, ``from_element`` and ``to_element`` always
    hold ``Reference | None``.
    """

    from_element: Reference | Element | UUID | None = infra(default=None)
    to_element: Reference | Element | UUID | None = infra(default=None)
    directed: bool = infra(default=True)

    def __post_init__(self, lat=None, lon=None) -> None:
        super().__post_init__(lat, lon)
        if self.from_element is not None and not isinstance(self.from_element, Reference):
            self.from_element = Reference(self.from_element)
        if self.to_element is not None and not isinstance(self.to_element, Reference):
            self.to_element = Reference(self.to_element)
