from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd
from shapely.geometry import Point
import pytz
from uuid import uuid4


def generate_id() -> str: 
    return "".join(random.choices(string.ascii_lowercase, k=12))


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


@dataclass
class EnergyAsset:
    name: Optional[str] = None
    location: Optional[Location] = None


@dataclass
class Site:
    assets: List[EnergyAsset] = field(default_factory=list)
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    altitude: Optional[float] = None 
    tz: Optional[pytz.timezone] = None
    location: Optional[Location] = None
    name: Optional[str] = None
    _id: str = field(init=False, repr=False, default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        if self.longitude is not None and self.latitude is not None:
            self.location = Location(longitude=self.longitude,
                                     latitude=self.latitude,
                                     altitude=self.altitude,
                                     tz=self.tz)

    def add_assets(self, assets: Union[EnergyAsset, List[EnergyAsset]]):
        if isinstance(assets, list):
            self.assets.extend(assets)
        else:
            self.assets.append(assets)

    def remove_asset(self, asset: EnergyAsset):
        self.assets.remove(asset)

    def list_assets(self):
        return self.assets
    
    def get_summary(self):
        summary = f"Name: {self.name}\n"
        summary += f"Site ID: {self._id}\n"
        summary += f"Location: {self.location}\n"
        summary += "Assets:\n"
        for asset in self.assets:
            summary += f"  - {asset.name}\n"
        return summary
    

@dataclass
class FixedMount:
    surface_tilt: float = 0.0
    surface_azimuth: float = 0.0


@dataclass
class SingleAxisTrackerMount: 
    axis_tilt: float = 0.0
    axis_azimuth: float = 0.0 
    max_angle: Union[float, tuple] = 90.0 
    backtrack: bool = True 
    gcr: float = 0.2857142857142857 
    cross_axis_tilt: float = 0.0 
    racking_model: Optional[str] = None
    module_height: Optional[float] = None


@dataclass
class PVArray(EnergyAsset):
    capacity: Optional[float] = None 
    efficiency: Optional[float] = None  # Efficiency in percentage
    area: Optional[float] = None        # Area in square meters
    module: Optional[str] = None
    module_type: str = "glass_polymer"
    module_parameters: Union[dict, pd.Series] = None
    temperature_model_parameters: Union[dict, pd.Series] = None


@dataclass
class PVSystem(EnergyAsset):
    arrays: List[PVArray] = None
    albedo: Optional[float] = None
    surface_type: Optional[str] = None


@dataclass
class EnergySystem:
    sites: List[Site] = field(default_factory=list)
    assets: List[EnergyAsset] = field(default_factory=list)

    def add_sites(self, sites: Union[Site, List[Site]]):
        if isinstance(sites, list):
            self.sites.extend(sites)
        else:
            self.sites.append(sites)

    def add_assets(self, assets: Union[EnergyAsset, List[EnergyAsset]]):
        if isinstance(assets, list):
            self.assets.extend(assets)
        else:
            self.assets.append(assets)

    def remove_site(self, site: Site):
        self.sites.remove(site)

    def remove_asset(self, asset: EnergyAsset):
        self.assets.remove(asset)

    def get_summary(self):
        def recursive_summary(site, level=0):
            summary = "  " * level + f"- {site.name}\n"
            for asset in site.assets:
                summary += "  " * (level + 1) + f"- {asset.name}\n"
            return summary

        summary = "=====================\n"
        summary += "Energy System Summary\n"
        summary += "====================="
        summary += "\nSites:\n"
        for site in self.sites:
            summary += f"- {site.name}\n"
            summary += "  " + f"{site.location}\n"

            for asset in site.assets:
                summary += "  " + f"- {asset.name}\n"
        summary += "\nNon-site assets:\n"
        for asset in self.assets:
            summary += f"- {asset.name}\n"
        summary += "=====================\n"
        return summary


# Example Usage
if __name__ == "__main__":
    site = Site(longitude=15, latitude=55, name="My Site")
    asset1 = EnergyAsset("Asset 1")
    asset2 = EnergyAsset("Asset 2")

    site.add_assets(asset1)
    site.add_assets(asset2)

    # Get and print the site summary
    site_summary = site.get_summary()
    print(site_summary)

    energy_system = EnergySystem()

    site1 = Site(longitude=15, latitude=55, name="Site 1")
    site2 = Site(longitude=25, latitude=65, name="Site 2")
    site1.add_assets([EnergyAsset("Asset 1"), EnergyAsset("Asset 2")])
    site2.add_assets(EnergyAsset("Asset 3"))

    energy_system.add_site(site1)
    energy_system.add_site(site2)
    energy_system.add_asset(EnergyAsset("Asset 4"))

    # Get and print the energy system summary
    system_summary = energy_system.get_summary()
    print(system_summary)
    print(site1)