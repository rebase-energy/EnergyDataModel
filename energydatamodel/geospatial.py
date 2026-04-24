"""Geospatial helper types.

These are value types (not :class:`Element` subclasses) — they carry
coordinates and geometry only, and can be used as inputs that get converted
into shapely geometries on Element. Shapely is the underlying truth for all
geometry storage on Element.
"""

from __future__ import annotations

import datetime
import json
from dataclasses import dataclass
from zoneinfo import ZoneInfo

import geopandas as gpd
import pvlib
from shapely.geometry import MultiPolygon, Point, Polygon


@dataclass(repr=False)
class GeoLocation:
    """Point location with a timezone and optional altitude.

    Convenience input value type. Convert to a shapely ``Point`` via
    :meth:`to_point` when populating an Element's ``geometry`` field.
    """

    longitude: float
    latitude: float
    tz: str | datetime.tzinfo = "UTC"
    altitude: float | None = None
    name: str | None = None

    def __post_init__(self):
        self.point = Point(self.longitude, self.latitude)
        if isinstance(self.tz, str):
            self.tz = ZoneInfo(self.tz)

    @classmethod
    def from_point(cls, point: Point):
        return cls(longitude=point.x, latitude=point.y)

    def to_tuple(self):
        return (self.latitude, self.longitude)

    @property
    def tuple(self):
        return self.to_tuple()

    def to_point(self) -> Point:
        """Return a shapely ``Point`` using ``(longitude, latitude)`` ordering.

        Use this to populate an Element's ``geometry`` field from a
        ``GeoLocation`` input.
        """
        return Point(self.longitude, self.latitude)

    def to_pvlib(self):
        return pvlib.location.Location(
            latitude=self.latitude,
            longitude=self.longitude,
            altitude=self.altitude,
            tz=self.tz,
        )


Location = GeoLocation


# GeoPolygon is just Shapely's Polygon — the historical ``@dataclass`` override
# didn't work cleanly on top of Shapely's C-ext type. Kept as a named alias so
# downstream type hints remain stable.
GeoPolygon = Polygon


@dataclass
class GeoMultiPolygon:
    """MultiPolygon wrapper (composition rather than inheritance)."""

    multipolygon: MultiPolygon = None
    name: str | None = None

    @classmethod
    def from_geojson(cls, file: str):
        multipolygon = gpd.read_file(file).loc[0, "geometry"]
        return cls(multipolygon=multipolygon)

    def to_geojson(self):
        return json.loads(json.dumps(self.multipolygon.__geo_interface__))

    @property
    def geojson(self):
        return self.to_geojson()
