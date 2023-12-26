from dataclasses import dataclass
from typing import Optional
from shapely.geometry import Point
import pytz


@dataclass
class Location:
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