"""Element — the root of the EDM type hierarchy.

``Element`` is the shared base for everything in the model. It carries the
fields that any persistable, named, geometry-bearing object needs:

* ``id`` — a stable UUID7, generated at construction
* ``name`` — human label (display / CLI navigation)
* ``timeseries`` — metadata-only ``TimeSeries`` declarations attached to
  this element (``df=None``; the actual data is written via the energydb
  data-write path, not carried inline on the EDM tree)
* ``geometry`` — optional shapely geometry (Point, Polygon, LineString, ...)
* ``extra`` — open dict of JSON-native scalars

Sibling subtrees specialize ``Element``:

* :class:`Node` (in :mod:`energydatamodel.node`) — anything that exists
  as a "thing": graph vertices, Areas, plus container markers.
  Adds ``members`` and ``tz``.
* :class:`Edge` (in :mod:`energydatamodel.edge`) — edges between
  two Nodes. Adds ``from_element``, ``to_element``, ``directed``.
* :class:`Asset` (in :mod:`energydatamodel.asset`) — mixin marking
  physical energy equipment. Mixed with ``Node`` or ``Edge`` via
  :class:`NodeAsset` / :class:`EdgeAsset`.
* :class:`Collection` (in :mod:`energydatamodel.containers`) — groupings
  that aren't graph vertices (Portfolio, Site, Region, ...).

Identity is a UUID7 assigned at construction. The same Element instance keeps
its ``id`` across renames and across JSON round-trips.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import InitVar, dataclass, field, fields
from typing import Any, cast, overload
from uuid import UUID

import pandas as pd
from shapely.geometry import LineString, Point, Polygon, mapping
from shapely.geometry.base import BaseGeometry
from timedatamodel import TimeSeries
from uuid6 import uuid7

# ---------------------------------------------------------------------
# Field-metadata helpers
# ---------------------------------------------------------------------
#
# Each Element field is tagged with one of two roles:
#
#   - "infra"    : framework-owned (id, name, geometry, timeseries, extra,
#                  members, tz, commissioning_date, from_element, ...).
#                  Excluded from ``to_properties()``.
#   - "domain"   : everything else. The default if no metadata is set.
#
# ``infra(children=True)`` additionally marks a children-bearing field
# (``members``), so that ``element_to_storage_dict`` can drop it when
# the row is written flat (children stored via FK in DB).
#
# Concrete subclasses don't need to mark their domain fields — only
# framework infra fields use ``infra(...)``.


@overload
def infra[T](*, default: T, children: bool = False) -> T: ...
@overload
def infra[T](*, default_factory: Callable[[], T], children: bool = False) -> T: ...
@overload
def infra(*, children: bool = False) -> Any: ...


def infra(
    *,
    default: Any = None,
    default_factory: Callable[[], Any] | None = None,
    children: bool = False,
) -> Any:
    """Build a dataclass ``field`` marked as framework infrastructure.

    Use in place of ``dataclasses.field`` for any non-domain attribute
    declared on an Element subclass::

        my_field: T = infra(default=None)
        members: list[Element] = infra(default_factory=list, children=True)
    """
    metadata = {"role": "infra", "children": children}
    if default_factory is not None:
        return cast(Any, field(default_factory=default_factory, metadata=metadata))
    return cast(Any, field(default=default, metadata=metadata))


def is_infra_field(f) -> bool:
    """``True`` if a dataclass field is framework infrastructure (excluded
    from :meth:`Element.to_properties`)."""
    return f.metadata.get("role") == "infra"


def is_children_field(f) -> bool:
    """``True`` if a dataclass field holds child Elements (excluded from
    flat storage rows)."""
    return f.metadata.get("children") is True


def _tree_repr(obj, prefix: str = "", is_last: bool = True, is_root: bool = True) -> str:
    """Render a tree representation of an Element hierarchy via ``.children()``."""
    name = getattr(obj, "name", None)
    label = f"{type(obj).__name__}('{name}')" if name else f"{type(obj).__name__}()"
    connector = "" if is_root else ("└── " if is_last else "├── ")
    lines = [prefix + connector + label]
    children = obj.children()
    child_prefix = prefix + ("" if is_root else ("    " if is_last else "│   "))
    for i, child in enumerate(children):
        lines.append(_tree_repr(child, child_prefix, i == len(children) - 1, is_root=False))
    return "\n".join(lines)


@dataclass(repr=False, kw_only=True)
class Element:
    """Common base for every persistable object in EDM.

    Identity is a UUID7 generated at construction. ``name`` is a mutable
    human label; renames don't change the ``id``.

    Subclasses are auto-registered for JSON dispatch via
    ``__init_subclass__`` — defining ``class Foo(NodeAsset): ...`` is enough
    for round-trip serialization, no decorator required.
    """

    id: UUID = field(default_factory=uuid7, metadata={"role": "infra"})
    name: str | None = field(default=None, metadata={"role": "infra"})
    timeseries: list[TimeSeries] = field(default_factory=list, metadata={"role": "infra"})
    geometry: BaseGeometry | None = field(default=None, metadata={"role": "infra"})
    # Free-form bag for ad-hoc scalar fields not modeled here. Restricted to
    # JSON-native scalars (str / int / float / bool / None) plus nested
    # dict / list of same. EDM types and enums are *not* allowed — define a
    # typed subclass instead.
    extra: dict = field(default_factory=dict, metadata={"role": "infra"})
    lat: InitVar[float | None] = None
    lon: InitVar[float | None] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Auto-register every Element subclass for JSON dispatch on definition.
        # Last-write-wins: re-running a class definition in a notebook creates
        # a new class object with the same name, and we want the latest one to
        # be authoritative — matches Python's own class-redefinition semantics.
        # Lazy import avoids the circular dependency with ``json_io``.
        from energydatamodel.json_io import _REGISTRY

        _REGISTRY[cls.__name__] = cls

    def __post_init__(self, lat: float | None, lon: float | None) -> None:
        if (lat is None) != (lon is None):
            raise ValueError("lat and lon must be provided together")
        if lat is not None:
            if self.geometry is not None:
                raise ValueError("pass either (lat, lon) or geometry, not both")
            self.geometry = Point(lon, lat)
        elif isinstance(self.geometry, (tuple, list)):
            if len(self.geometry) != 2 or not all(isinstance(v, (int, float)) for v in self.geometry):
                raise ValueError("geometry tuple shorthand must be (lon, lat) of two numbers")
            self.geometry = Point(self.geometry[0], self.geometry[1])
        if self.geometry is not None:
            minx, miny, maxx, maxy = self.geometry.bounds
            if not (minx >= -180 and maxx <= 180 and miny >= -90 and maxy <= 90):
                raise ValueError(
                    f"geometry bounds {self.geometry.bounds} fall outside "
                    "WGS84 lon/lat range — did you swap lat and lon?"
                )

    # ------------------------------------------------------------------ shape
    @property
    def latitude(self) -> float | None:
        """Latitude, if ``geometry`` is a shapely ``Point``; else ``None``."""
        if isinstance(self.geometry, Point):
            return self.geometry.y
        return None

    @property
    def longitude(self) -> float | None:
        """Longitude, if ``geometry`` is a shapely ``Point``; else ``None``."""
        if isinstance(self.geometry, Point):
            return self.geometry.x
        return None

    @property
    def centroid(self) -> Point | None:
        """Centroid of ``geometry``, or ``None`` if no geometry."""
        if self.geometry is None:
            return None
        return self.geometry.centroid

    # ------------------------------------------------------------------ tree
    def children(self) -> list:
        """Child elements for tree walking. Override in subclasses with children."""
        return []

    def add_child(self, obj) -> None:
        """Attach a child. Override in subclasses that support children."""
        raise TypeError(
            f"{type(self).__name__} does not support add_child(). Override add_child() to enable tree reconstruction."
        )

    def to_tree(self) -> str:
        """Return the hierarchy rendered as an indented tree string.

        Use ``print(element.to_tree())`` to display it. In a notebook, printing
        the element directly (``element``) also renders the tree via ``__repr__``.
        """
        return _tree_repr(self)

    def index(self):
        """Build a ``dict[UUID, Element]`` index of the subtree rooted at self.

        Use to resolve :class:`Reference` objects against this tree.
        """
        from energydatamodel.reference import build_index

        return build_index(self)

    # --------------------------------------------------------------- props
    def to_properties(self) -> dict:
        """Domain-specific fields as a dict (excludes infra + children fields)."""
        props: dict = {}
        for f in fields(self):
            if is_infra_field(f):
                continue
            value = getattr(self, f.name)
            if value is None:
                continue
            # Empty containers also skipped (empty lists/dicts are noise).
            if isinstance(value, (list, dict)) and len(value) == 0:
                continue
            props[f.name] = value
        return props

    # --------------------------------------------------------------- json
    def to_json(self, *, exclude_fields: set | None = None) -> dict:
        """Serialize to a JSON-compatible dict."""
        from energydatamodel.json_io import element_to_json

        return element_to_json(self, exclude_fields=exclude_fields)

    @classmethod
    def from_json(cls, data: dict) -> Element:
        """Deserialize from a JSON-compatible dict."""
        from energydatamodel.json_io import element_from_json

        return element_from_json(data, expected_type=cls)

    # ------------------------------------------------------------- geojson
    def geometry_to_geojson(self, geometry):
        if isinstance(geometry, Point):
            return {"type": "Point", "coordinates": list(geometry.coords)[0]}
        elif isinstance(geometry, Polygon):
            return {"type": "Polygon", "coordinates": [list(geometry.exterior.coords)]}
        elif isinstance(geometry, LineString):
            return {"type": "LineString", "coordinates": list(geometry.coords)}
        return None

    def to_geojson(self, exclude_none: bool = True):
        features = list(self._collect_geojson_features(exclude_none=exclude_none))
        if len(features) == 1:
            return features[0]
        return {"type": "FeatureCollection", "features": features}

    def _collect_geojson_features(self, exclude_none: bool = True):
        """Yield flat Feature dicts from this element and its descendants."""
        children = self.children()
        if children:
            for child in children:
                yield from child._collect_geojson_features(exclude_none=exclude_none)
        else:
            geojson_geometry, geojson_properties = self._extract_geojson_data(self, exclude_none)
            if geojson_geometry:
                yield {
                    "type": "Feature",
                    "geometry": geojson_geometry,
                    "properties": geojson_properties,
                }

    def _extract_geojson_data(self, obj, exclude_none: bool = True):
        geojson_geometry = None
        geojson_properties: dict = {}
        for attr_name, attr_value in obj.__dict__.items():
            if isinstance(attr_value, BaseGeometry):
                geojson_geometry = mapping(attr_value)
            elif isinstance(attr_value, pd.DataFrame):
                continue
            elif hasattr(attr_value, "__dict__"):
                nested_geometry, nested_properties = self._extract_geojson_data(attr_value)
                if nested_geometry:
                    geojson_geometry = nested_geometry
                geojson_properties.update(nested_properties)
            else:
                if not (exclude_none and attr_value is None):
                    geojson_properties[attr_name] = attr_value
        return geojson_geometry, geojson_properties

    # ---------------------------------------------------------------- misc
    def to_dataframe(self):
        data = {f.name: getattr(self, f.name) for f in fields(self)}
        return pd.DataFrame({self.__class__.__name__: data})

    def __repr__(self):
        return _tree_repr(self)
