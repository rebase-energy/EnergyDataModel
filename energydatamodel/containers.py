"""Collection marker and container subclasses.

:class:`Collection` is an :class:`Element` whose primary purpose is grouping
other elements. It is **not** a :class:`Node` — collections aren't graph
vertices; they're organizational/logical groupings. Collection shares the
``members`` and ``tz`` field shape with Node, but the semantics differ —
``isinstance(x, Node)`` on a Portfolio should return False.

Concrete subclasses carry no additional fields; they distinguish a Portfolio
from a Site at the type level for serialization / introspection / UI.

Conventions:

* ``Portfolio`` — trading/asset aggregate. Typically no geometry.
* ``Site`` — a geographic site containing assets. Typically a ``Point`` geometry.
* ``MultiSite`` — group of sites.
* ``Region`` — a named geographic region with a ``Polygon`` / ``MultiPolygon``
  geometry. (Distinct from :class:`Area`: regions are not bound to a market /
  administrative scope.)
* ``EnergyCommunity`` — members share resources/balance.
* ``VirtualPowerPlant`` — traded flexibility aggregate.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import ClassVar, List, Optional

from energydatamodel.element import Element


@dataclass(repr=False, kw_only=True)
class Collection(Element):
    """An Element whose primary purpose is grouping other Elements.

    Not a :class:`Node` — collections are organizational groupings, not graph
    vertices. Carries ``members`` and ``tz`` (same shape as Node, different
    semantics).
    """

    members: List[Element] = field(default_factory=list)
    tz: Optional[datetime.tzinfo] = None

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


@dataclass(repr=False, kw_only=True)
class Portfolio(Collection):
    """A trading/asset portfolio aggregate."""


@dataclass(repr=False, kw_only=True)
class Site(Collection):
    """A geographic site containing one or more assets."""


@dataclass(repr=False, kw_only=True)
class MultiSite(Collection):
    """An aggregate of multiple sites."""


@dataclass(repr=False, kw_only=True)
class Region(Collection):
    """A named geographic region — typically backed by a Polygon geometry.

    Distinct from :class:`Area`: a Region is not labeled by market or
    administrative scope; it's a freeform geographic grouping.
    """


@dataclass(repr=False, kw_only=True)
class EnergyCommunity(Collection):
    """An energy community — members share resources/balance."""


@dataclass(repr=False, kw_only=True)
class VirtualPowerPlant(Collection):
    """A virtual power plant — traded flexibility aggregate."""
