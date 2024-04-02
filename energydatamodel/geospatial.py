from dataclasses import dataclass
from typing import Optional, List, Union
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
import pytz
import json
import geopandas as gpd

from energydatamodel import BaseClass

@dataclass(repr=False)
class GeoLocation(BaseClass):
    """This is the docstring for Location."""

    longitude: float
    latitude: float
    altitude: Optional[float] = None
    tz: Optional[pytz.timezone] = None
    name: Optional[str] = None

    def __post_init__(self):
        self.point = Point(self.latitude, self.longitude)

    @classmethod
    def from_point(cls, point: Point):
        return cls(longitude=point.x, latitude=point.y)

    def to_tuple(self):
        return (self.latitude, self.longitude)

    @property
    def tuple(self):
        return self.to_tuple()

Location = GeoLocation

@dataclass
class GeoLine(BaseClass, LineString):
    """This is the docstring for LineString."""

@dataclass
class GeoPolygon(BaseClass, Polygon):
    """This is the docstring for Polygon."""

    name: Optional[str] = None

#TODO I think it would be nicer if GeoMultiPolygon was a subclass of MultiPolygon instead of composition. 
@dataclass
class GeoMultiPolygon(BaseClass):
    """This is the docstring for Polygon."""
    multipolygon: MultiPolygon = None
    name: Optional[str] = None

    @classmethod
    def from_geojson(cls, file: str):
        multipolygon = gpd.read_file(file).loc[0, "geometry"]
        return cls(multipolygon=multipolygon)

    def to_geojson(self):
        return json.loads(json.dumps(self.multipolygon.__geo_interface__))

    @property
    def geojson(self):
        return self.to_geojson()

@dataclass
class GeoGraph(BaseClass):
    """This is the docstring for GeoGraph."""

    name: Optional[str] = None