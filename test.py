from dataclasses import dataclass
from shapely.geometry import Point

@dataclass
class Location:
    lon: float
    lat: float

    def __post_init__(self):
        # If lon and lat are provided, create a Point object
        self.point = Point(self.lon, self.lat)

    @classmethod
    def from_point(cls, point: Point):
        return cls(point.x, point.y)

# Example usage:

# Initialize using longitude and latitude
location1 = Location(lon=123.45, lat=67.89)
print(location1.lon, location1.lat)  # Prints: 123.45 67.89
print(location1.point)  # Prints: POINT (123.45 67.89)

# Initialize using a Shapely Point object
point = Point(111.11, 55.55)
location2 = Location.from_point(point)
print(location2.lon, location2.lat)  # Prints: 111.11 55.55
print(location2.point)  # Prints: POINT (111.11 55.55)
