"""Node — the "vertex" subtree of EDM.

A Node is anything that exists as a graph vertex in the model: a piece of
equipment, an administrative area, a grid topology point, or a sensor. Adds
two fields to :class:`Element`:

* ``members`` — child elements (used by WindFarm, Network, etc.)
* ``tz`` — local timezone, where meaningful

Equipment-shaped vertices (WindTurbine, Battery, Sensor, GridNode, ...) mix
:class:`Asset` via :class:`NodeAsset` in :mod:`energydatamodel.bases`.
Edges between nodes live in the sibling :class:`Edge` subtree. Logical
groupings (Portfolio, Site, ...) live in :class:`Collection`, which is a
sibling of Node under :class:`Element` — not a subclass of Node.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import ClassVar

from energydatamodel.element import Element


@dataclass(repr=False, kw_only=True)
class Node(Element):
    """An Element that exists as a graph vertex — can hold members and a timezone.

    Subclassed by NodeAsset (equipment) and Area (administrative regions).
    """

    members: list[Element] = field(default_factory=list)
    tz: datetime.tzinfo | None = None

    _BASE_FIELDS: ClassVar[frozenset] = Element._BASE_FIELDS | frozenset({
        "members", "tz",
    })
    _CHILDREN_FIELDS: ClassVar[frozenset] = frozenset({"members"})

    def children(self) -> list:
        return list(self.members)

    def add_child(self, obj: Element) -> None:
        if not isinstance(obj, Element):
            raise TypeError(
                f"{type(self).__name__} only accepts Element children, "
                f"got {type(obj).__name__}"
            )
        self.members.append(obj)
