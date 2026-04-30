"""Edge — the "relationship" subtree of EDM.

An ``Edge`` is an edge between two :class:`Node` instances: a line between
two buses, an interconnector between two bidding zones, a transformer
between two buses, a pipe between two delivery points. Edges sit sibling to
``Node`` under :class:`Element`, not under ``Node`` — this keeps ``members``
and ``tz`` off Edges, where they don't apply.

Concrete edge-equipment subclasses (Line, Link, Transformer, Pipe,
Interconnection) live in :mod:`energydatamodel.grid` under
:class:`EdgeAsset`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from energydatamodel.element import Element
from energydatamodel.reference import Reference

if TYPE_CHECKING:
    from energydatamodel.node import Node


@dataclass(repr=False, kw_only=True)
class Edge(Element):
    """An edge between two Nodes.

    Edges are **always directed by convention** — flow in the opposite
    direction is expressed as a signed value on the timeseries. The ``directed``
    flag is kept for explicit cases (e.g. pure bidirectional pipes).
    """

    from_entity: Reference[Node] | None = None
    to_entity: Reference[Node] | None = None
    directed: bool = True

    _BASE_FIELDS: ClassVar[frozenset] = Element._BASE_FIELDS | frozenset(
        {
            "from_entity",
            "to_entity",
            "directed",
        }
    )
