from dataclasses import dataclass
from typing import Optional, List, Union
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
import pytz
import json
import geopandas as gpd
import pvlib

from energydatamodel import AbstractClass

@dataclass(repr=False)
class GeoLocation(AbstractClass):
    """This is the docstring for Location."""

    longitude: float
    latitude: float
    tz: Union[str, pytz.timezone] = "UTC"
    altitude: Optional[float] = None
    name: Optional[str] = None

    def __post_init__(self):
        self.point = Point(self.latitude, self.longitude)

        if isinstance(self.tz, str):
            self.tz = pytz.timezone(self.tz)

    @classmethod
    def from_point(cls, point: Point):
        return cls(longitude=point.x, latitude=point.y)

    def to_tuple(self):
        return (self.latitude, self.longitude)

    @property
    def tuple(self):
        return self.to_tuple()
    
    def to_pvlib(self):
        return pvlib.location.Location(latitude=self.latitude, longitude=self.longitude, altitude=self.altitude, tz=self.tz)

Location = GeoLocation

@dataclass
class GeoLine(AbstractClass, LineString):
    """This is the docstring for LineString."""

@dataclass
class GeoPolygon(AbstractClass, Polygon):
    """This is the docstring for Polygon."""

    name: Optional[str] = None

#TODO I think it would be nicer if GeoMultiPolygon was a subclass of MultiPolygon instead of composition. 
@dataclass
class GeoMultiPolygon(AbstractClass):
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
class GeoGraph(AbstractClass):
    """This is the docstring for GeoGraph."""

    name: Optional[str] = None