"""Element — the root of the EDM type hierarchy.

``Element`` is the shared base for everything in the model. It carries the
fields that any persistable, named, geometry-bearing object needs:

* ``name``, ``_id`` — identity
* ``timeseries`` — descriptors of attached time series
* ``geometry`` — optional shapely geometry (Point, Polygon, LineString, ...)

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

``Element`` is abstract in spirit (never instantiated directly) but is a
concrete dataclass so subclasses can ``super().__init__(...)`` cleanly.
"""

from __future__ import annotations

import dataclasses
from dataclasses import InitVar, dataclass, field, fields
from typing import ClassVar

import pandas as pd
from shapely.geometry import LineString, Point, Polygon, mapping
from shapely.geometry.base import BaseGeometry
from timedatamodel import TimeSeriesDescriptor


def _tree_repr(obj, prefix: str = "", is_last: bool = True, is_root: bool = True) -> str:
    """Render a tree representation of an Element hierarchy via ``.children()``."""
    name = getattr(obj, "name", None)
    label = f"{type(obj).__name__}('{name}')" if name else f"{type(obj).__name__}()"
    connector = "" if is_root else ("\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 ")
    lines = [prefix + connector + label]
    children = obj.children()
    child_prefix = prefix + ("" if is_root else ("    " if is_last else "\u2502   "))
    for i, child in enumerate(children):
        lines.append(_tree_repr(child, child_prefix, i == len(children) - 1, is_root=False))
    return "\n".join(lines)


@dataclass(repr=False, kw_only=True)
class Element:
    """Common base for every persistable object in EDM.

    Carries the fields shared by Nodes, Edges, Assets and Collections:
    name, id, attached time-series descriptors, an optional shapely
    geometry, and an ``extra`` dict for ad-hoc fields.

    Subclasses are auto-registered for JSON dispatch via
    ``__init_subclass__`` — defining ``class Foo(NodeAsset): ...`` is enough
    for round-trip serialization, no decorator required.
    """

    name: str | None = None
    _id: str | None = None
    timeseries: list[TimeSeriesDescriptor] = field(default_factory=list)
    geometry: BaseGeometry | None = None
    # Free-form bag for ad-hoc fields not modeled here. Round-trips through JSON
    # as long as values are JSON-native, shapely geometries, enums, dataclasses,
    # or other registered EDM types — other types fall through to ``repr()``.
    extra: dict = field(default_factory=dict)
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

    # Fields excluded from ``to_properties()`` — stored as top-level DB columns
    # or handled by the serialization layer directly.
    _BASE_FIELDS: ClassVar[frozenset] = frozenset(
        {
            "name",
            "_id",
            "timeseries",
            "geometry",
            "extra",
        }
    )
    # Fields that hold child objects — excluded from ``to_properties()``.
    _CHILDREN_FIELDS: ClassVar[frozenset] = frozenset()

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

    # --------------------------------------------------------------- props
    def to_properties(self) -> dict:
        """Domain-specific fields as a dict (excludes base + children fields)."""
        exclude = self._BASE_FIELDS | self._CHILDREN_FIELDS
        props = {}
        for f in dataclasses.fields(self):
            if f.name in exclude:
                continue
            value = getattr(self, f.name)
            if value is None:
                continue
            # Empty containers also skipped (empty members list on a leaf is noise).
            if isinstance(value, (list, dict)) and len(value) == 0:
                continue
            props[f.name] = value
        return props

    # --------------------------------------------------------------- json
    def to_json(
        self,
        include_ids: bool = False,
        *,
        exclude_fields: set | None = None,
    ) -> dict:
        """Serialize to a JSON-compatible dict. Full implementation in ``json_io``."""
        from energydatamodel.json_io import element_to_json

        return element_to_json(self, include_ids=include_ids, exclude_fields=exclude_fields)

    @classmethod
    def from_json(cls, data: dict) -> Element:
        """Deserialize from a JSON-compatible dict. Full implementation in ``json_io``."""
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
