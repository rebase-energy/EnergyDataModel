from dataclasses import dataclass
from typing import Optional, List, Union
from shapely.geometry import Point, LineString, Polygon
import pytz


@dataclass
class GeoLocation:
    """This is the docstring for Location."""

    longitude: float
    latitude: float
    altitude: Optional[float] = None
    tz: Optional[pytz.timezone] = None
    name: Optional[str] = None

    def __post_init__(self):
        self.point = Point(self.longitude, self.latitude)

    @classmethod
    def from_point(cls, point: Point):
        return cls(point.x, point.y)


Location = GeoLocation

@dataclass
class LineString(LineString):
    """This is the docstring for LineString."""


@dataclass
class Polygon(Polygon):
    """This is the docstring for Polygon."""

    name: Optional[str] = None