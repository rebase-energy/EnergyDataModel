"""Node — the "vertex" subtree of EDM.

A Node is anything that exists as a thing in the model: a physical asset,
a grid topology node, a sensor, an administrative area, or a container that
groups other nodes. Adds two fields to :class:`Entity`:

* ``members`` — child entities (used by Site, Portfolio, WindFarm, etc.)
* ``tz`` — local timezone, where meaningful

Edges between nodes live in the sibling :class:`Edge` subtree, not
under ``Node``. This split keeps ``members`` and ``tz`` off the Edge
type where they don't apply.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, List, Optional

import pytz

from energydatamodel.entity import Entity


@dataclass(repr=False, kw_only=True)
class Node(Entity):
    """An Entity that exists as a thing — can hold members and a timezone.

    Subclassed by Asset, GridNode, Sensor, Area, and the Collection marker
    class (Portfolio, Site, Region, ...).
    """

    members: List[Entity] = field(default_factory=list)
    tz: Optional[pytz.BaseTzInfo] = None

    _BASE_FIELDS: ClassVar[frozenset] = Entity._BASE_FIELDS | frozenset({
        "members", "tz",
    })
    _CHILDREN_FIELDS: ClassVar[frozenset] = frozenset({"members"})

    def children(self) -> list:
        return list(self.members)

    def add_child(self, obj: Entity) -> None:
        if not isinstance(obj, Entity):
            raise TypeError(
                f"{type(self).__name__} only accepts Entity children, "
                f"got {type(obj).__name__}"
            )
        self.members.append(obj)
