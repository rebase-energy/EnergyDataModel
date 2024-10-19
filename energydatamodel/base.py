import dataclasses
from dataclasses import dataclass, field, fields
import typing as t
import pandas as pd
import matplotlib.pyplot as plt
import shapely
from shapely.geometry import mapping, Point, Polygon, LineString
import pytz
from uuid import uuid4
from anytree import Node, RenderTree

import energydatamodel as edm
from energydatamodel import AbstractClass, Location

@dataclass(repr=False, kw_only=True)
class TimeSeries(AbstractClass):
    name: t.Optional[str] = None
    df: t.Optional[pd.DataFrame] = None
    column_names: t.Optional[t.Union[str, int, t.Tuple[str], t.Tuple[int]]] = None
    filename: t.Optional[str] = None

    def get_data(self) -> pd.Series: 
        """
        Get data from :class:`TimeSeries` as a :class:`pandas.Series`.

        Returns:
            The time series data. 
        """

        s = self.df.loc[:, [self.column_name]]
        return s

    def plot(self, start_date: t.Union[str, pd.DatetimeIndex], end_date: t.Union[str, pd.DatetimeIndex]) -> plt.Axes: 
        """
        Plots a pandas Series using its built-in plot method.

        Args:
            start_date: The start date for the plot. 
            end_date: The end date for the plot. 
            
        Returns:
            The Matplotlib Axes object of the plot.
        """

        series = self.df.loc[start_date:end_date, [self.column_name]]
        ax = series.plot()

        return ax


@dataclass(repr=False, kw_only=True)
class EnergyAsset(AbstractClass):
    """Get data from :class: `TimeSeries`"""

    name: t.Optional[str] = None
    location: t.Optional[Location] = None
    latitude: t.Optional[float] = None
    longitude: t.Optional[float] = None
    altitude: t.Optional[float] = None
    tz: t.Optional[pytz.timezone] = None
    timeseries: t.Optional[TimeSeries] = None

    def __post_init__(self):
        if self.location is None: 
            if self.longitude is not None and self.latitude is not None:
                self.location = Location(self.longitude, self.latitude)
            if self.altitude is not None: 
                self.location.altitude = self.altitude
            if self.tz is not None: 
                self.location.tz = self.tz

    def plot_timeseries(self, 
                        start_date: t.Optional[t.Union[str, pd.DatetimeIndex]] = None, 
                        end_date: t.Optional[t.Union[str, pd.DatetimeIndex]] = None) -> plt.Axes: 
        """
        Plots a pandas Series using its built-in plot method.

        Args:
            start_date: The start date for the plot. 
            end_date: The end date for the plot. 
            
        Returns:
            The Matplotlib Axes object of the plot.
        """

        df = self.timeseries.df.loc[start_date:end_date, [self.timeseries.column_name]]
        ax = df.plot()

        return ax

@dataclass(repr=False, kw_only=True)
class EnergyCollection(AbstractClass):
    """EnergySystem base class."""

    name: t.Optional[str] = None
    assets: t.Optional[t.List[EnergyAsset]] = None

    def add_assets(self, assets: t.Union[EnergyAsset, t.List[EnergyAsset]]):
        if isinstance(assets, list):
            self.assets.extend(assets)
        else:
            self.assets.append(assets)

    def remove_asset(self, asset: EnergyAsset):
        self.assets.remove(asset)

    def list_assets(self):
        return self.assets
    
    def get_asset_by_name(self, name: str):
        for asset in self.assets:
            if asset.name == name:
                return asset
        return None
    
    def _build_tree(self, obj, parent=None, only_named=True):
        """
        Recursively builds an anytree tree structure from any object `obj`.
        This version inspects all attributes of the object and looks for objects or lists of objects.
        """
        # Create a node for the current object
        node = Node(obj.name, parent=parent, type=type(obj).__name__)

        # Inspect all attributes of the object
        for attr_name in dir(obj):
            # Skip special or private attributes (like __init__, __str__)
            if attr_name.startswith('__'):
                continue
            
            attr_value = getattr(obj, attr_name)

            # If the attribute is a list, iterate over its items
            if isinstance(attr_value, list):
                for item in attr_value:
                    # If the item is an object (class instance), recursively build the tree
                    if hasattr(item, 'name'):
                        if only_named:
                            if item.name:
                                self._build_tree(item, node, only_named=only_named)
                        else:
                            self._build_tree(item, node, only_named=only_named)

            # If the attribute is a single object, recursively build the tree
            elif hasattr(attr_value, 'name'):
                if only_named:
                    if attr_value.name:
                        self._build_tree(attr_value, node)
                else:
                    self._build_tree(attr_value, node)

        return node
    
    def draw_tree(self, only_named=True, show_type=False):
        # Render the tree
        tree = self._build_tree(self, only_named=only_named)

        for pre, fill, node in RenderTree(tree):
            if show_type:
                print(f"{pre}{node.name} ({node.type})")
            else:
                print(f"{pre}{node.name}")

  
@dataclass(kw_only=True)
class Sensor(AbstractClass):
    name: t.Optional[str] = None
    location: t.Optional[Location] = None