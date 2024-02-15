from dataclasses import dataclass, field
from typing import List, Optional, Union
import typing as t
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
import pytz
from uuid import uuid4
import ipywidgets as widgets
from IPython.display import display, HTML

from energydatamodel import BaseClass
from energydatamodel import Location, EnergyAsset


@dataclass
class Site(BaseClass):
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
    

@dataclass(repr=False)
class EnergySystem(BaseClass):
    sites: List[Site] = field(default_factory=list)
    assets: List[EnergyAsset] = field(default_factory=list)
    name: Optional[str] = None

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


@dataclass(repr=False)
class EnergyCommunity(EnergySystem):
    """
    A Portfolio is like an EnergySystem but is used more for the purpose of trading energy rather than maintaining an energy balance. 
    """


@dataclass(repr=False)
class Portfolio(EnergySystem):
    """
    A Portfolio is like an EnergySystem but is used more for the purpose of trading energy rather than maintaining an energy balance. 
    """

    def plot_timeseries(self, start_date: t.Optional[str] = None, end_date: t.Optional[str] = None, subplots: bool = False) -> Union[t.Tuple[plt.Figure, plt.Axes], t.Tuple[plt.Figure, np.ndarray]]:
        # Convert start_date and end_date to datetime if they are not None
        if start_date is not None:
            start_date = pd.to_datetime(start_date)
        if end_date is not None:
            end_date = pd.to_datetime(end_date)

        # Create a single plot or subplots based on the subplots parameter
        if subplots:
            fig, axes = plt.subplots(len(self.assets), 1, sharex=True, figsize=(10, len(self.assets) * 3))
            for i, asset in enumerate(self.assets):
                column = asset.timeseries.column_name
                df = asset.timeseries.df
                # Slice the dataframe for the date range
                df_filtered = df.loc[start_date:end_date, column]
                if isinstance(axes, np.ndarray):
                    ax = axes[i]
                else:
                    ax = axes
                df_filtered.plot(ax=ax)
            plt.tight_layout()
            return fig, axes
        else:
            fig, ax = plt.subplots()
            for asset in self.assets:
                column = asset.timeseries.column_name
                df = asset.timeseries.df
                # Slice the dataframe for the date range
                df_filtered = df.loc[start_date:end_date, column]
                df_filtered.plot(ax=ax)
            return fig, ax




@dataclass(repr=False)
class VirtualPowerPlant(EnergySystem):
    """
    A VirtualPowerPlant is like an EnergySystem but is used more for the purpose of trading flexibility rather than maintaining an energy balance. 
    """
    pass