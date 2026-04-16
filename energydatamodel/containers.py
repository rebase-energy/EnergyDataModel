"""Collection marker and container subclasses.

:class:`Collection` is a :class:`Node` whose primary purpose is grouping
other entities. It adds no fields — it exists as a semantic marker for
``isinstance(x, Collection)`` checks and UI/API grouping.

Concrete subclasses carry no additional fields either; they distinguish
a Portfolio from a Site at the type level for serialization / introspection
/ UI.

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

from dataclasses import dataclass

from energydatamodel.node import Node


@dataclass(repr=False, kw_only=True)
class Collection(Node):
    """Marker for entities whose primary purpose is grouping other entities."""


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
