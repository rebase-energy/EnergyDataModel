from dataclasses import dataclass, field
from typing import List, Optional, Union
import typing as t
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
import pytz
from uuid import uuid4

from energydatamodel import AbstractClass, Location, EnergyAsset, EnergyCollection


@dataclass
class Site(EnergyCollection):
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
class MultiSite(EnergyCollection):
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

    def children(self) -> list:
        return (self.sites or []) + (self.assets or [])

    def add_child(self, obj) -> None:
        if isinstance(obj, Site):
            self.sites.append(obj)
        elif isinstance(obj, EnergyAsset):
            self.assets.append(obj)
        else:
            raise TypeError(f"MultiSite only accepts Site or EnergyAsset children, got {type(obj).__name__}")


@dataclass(repr=False)
class EnergyCommunity(EnergyCollection):
    """
    A Portfolio is like an EnergySystem but is used more for the purpose of trading energy rather than maintaining an energy balance. 
    """


@dataclass(repr=False)
class Portfolio(EnergyCollection):
    """
    A Portfolio is like an EnergySystem but is used more for the purpose of trading energy rather than maintaining an energy balance. 
    """

    def _asset_timeseries_to_pandas(self, asset, start_date=None, end_date=None):
        """Concatenate all timeseries entries of an asset into one DataFrame."""
        frames = []
        for ts in asset.timeseries:
            df = ts.to_pandas()
            if isinstance(df, pd.Series):
                df = df.to_frame()
            if ts.name:
                if len(df.columns) == 1:
                    df.columns = [ts.name]
                else:
                    df.columns = [f"{ts.name}.{c}" for c in df.columns]
            frames.append(df)
        combined = pd.concat(frames, axis=1)
        return combined.loc[start_date:end_date]

    def plot_timeseries(self, start_date: t.Optional[str] = None, end_date: t.Optional[str] = None, subplots: bool = False) -> Union[t.Tuple[plt.Figure, plt.Axes], t.Tuple[plt.Figure, np.ndarray]]:
        assets_with_data = [a for a in self.assets if a.timeseries]
        if not assets_with_data:
            raise ValueError("No assets with timeseries data in this portfolio.")

        if subplots:
            fig, axes = plt.subplots(len(assets_with_data), 1, sharex=True, figsize=(10, len(assets_with_data) * 3))
            for i, asset in enumerate(assets_with_data):
                df = self._asset_timeseries_to_pandas(asset, start_date, end_date)
                ax = axes[i] if isinstance(axes, np.ndarray) else axes
                df.plot(ax=ax)
                ax.set_title(asset.name or f"Asset {i}")
            plt.tight_layout()
            return fig, axes
        else:
            fig, ax = plt.subplots()
            for asset in assets_with_data:
                df = self._asset_timeseries_to_pandas(asset, start_date, end_date)
                df.columns = [f"{asset.name}.{col}" for col in df.columns]
                df.plot(ax=ax)
            return fig, ax




@dataclass(repr=False)
class VirtualPowerPlant(EnergyCollection):
    """
    A VirtualPowerPlant is like an EnergySystem but is used more for the purpose of trading flexibility rather than maintaining an energy balance. 
    """
    pass