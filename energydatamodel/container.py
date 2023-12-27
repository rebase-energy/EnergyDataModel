from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd
from shapely.geometry import Point
import pytz
from uuid import uuid4

from energydatamodel import Location, EnergyAsset


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


@dataclass
class Portfolio(EnergySystem):
    """
    A Portfolio is like an EnergySystem but is used more for the purpose of trading energy rather than maintaining an energy balance. 
    """


@dataclass
class VirtualPowerPlant(EnergySystem):
    """
    A VirtualPowerPlant is like an EnergySystem but is used more for the purpose of trading flexibility rather than maintaining an energy balance. 
    """