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
from energydatamodel.timeseries import TimeSeries, TimeSeriesTable

import energydatamodel as edm
from energydatamodel import AbstractClass, Location


@dataclass(repr=False, kw_only=True)
class EnergyAsset(AbstractClass):
    """Base class for all energy assets.

    The ``timeseries`` field holds an optional list of
    :class:`timedatamodel.TimeSeries` and/or :class:`timedatamodel.TimeSeriesTable`
    objects.  Each entry is either a univariate ``TimeSeries`` (single signal) or
    a multivariate ``TimeSeriesTable`` (multiple co-indexed signals).
    """

    name: t.Optional[str] = None
    location: t.Optional[Location] = None
    latitude: t.Optional[float] = None
    longitude: t.Optional[float] = None
    altitude: t.Optional[float] = None
    tz: t.Optional[pytz.timezone] = None
    timeseries: t.Optional[t.List[t.Union[TimeSeries, TimeSeriesTable]]] = None

    def __post_init__(self):
        if self.location is None:
            if self.longitude is not None and self.latitude is not None:
                self.location = Location(self.longitude, self.latitude)
            if self.altitude is not None:
                self.location.altitude = self.altitude
            if self.tz is not None:
                self.location.tz = self.tz

    def get_location(self):
        return self.location

    def plot_timeseries(self,
                        columns: t.Optional[t.List[str]] = None,
                        start_date: t.Optional[str] = None,
                        end_date: t.Optional[str] = None) -> plt.Axes:
        """Plot signals from the asset's timeseries list.

        Each entry in ``self.timeseries`` is converted to a pandas DataFrame,
        column names are prefixed with the entry's name (if set) to avoid
        collisions, and the results are concatenated before plotting.

        Args:
            columns: Signal names to plot. Defaults to all columns.
            start_date: ISO 8601 start date string for slicing (inclusive).
            end_date: ISO 8601 end date string for slicing (inclusive).

        Returns:
            The Matplotlib Axes object of the plot.
        """
        if not self.timeseries:
            raise ValueError("No timeseries data attached to this asset.")

        frames = []
        for ts in self.timeseries:
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

        if columns is not None:
            combined = combined[columns]

        if start_date is not None or end_date is not None:
            combined = combined.loc[start_date:end_date]

        ax = combined.plot()
        ax.set_ylabel("Value")
        ax.set_title(self.name or self.__class__.__name__)

        return ax

@dataclass(repr=False, kw_only=True)
class EnergyCollection(AbstractClass):
    """EnergySystem base class."""

    name: t.Optional[str] = None
    assets: t.Optional[t.List[EnergyAsset]] = field(default_factory=list)
    collections: t.Optional[t.List["EnergyCollection"]] = field(default_factory=list)

    def add_assets(self, assets: t.Union[EnergyAsset, t.List[EnergyAsset]]):
        if isinstance(assets, list):
            self.assets.extend(assets)
        else:
            self.assets.append(assets)

    def remove_asset(self, asset: EnergyAsset):
        self.assets.remove(asset)

    def list_assets(self):
        return self.assets
    
    def add_collection(self, collection: "EnergyCollection"):
        if isinstance(collection, list):
            self.collections.extend(collection)
        else:
            self.collections.append(collection)

    def list_collections(self):
        return self.collections
    
    def remove_collection(self, collection: "EnergyCollection"):
        self.collections.remove(collection)
    
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
        class_name = obj.__class__.__name__
        class_module = obj.__class__.__module__.split(".")[0]
        module_shorts = {"energydatamodel": "edm", "numpy": "np", "pandas": "pd"}

        node = Node(obj.name, parent=parent, type=f"{module_shorts[class_module]}.{class_name}")

        # Inspect all attributes of the object
        for attr_name in dir(obj):
            # Skip special or private attributes (like __init__, __str__)
            if attr_name.startswith('__'):
                continue
            
            attr_value = getattr(obj, attr_name)

            # Skip timeseries data containers
            if isinstance(attr_value, (TimeSeries, TimeSeriesTable)):
                continue
            if isinstance(attr_value, list) and attr_value and isinstance(attr_value[0], (TimeSeries, TimeSeriesTable)):
                continue

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
    
    def to_tree(self, only_named=True, show_type=False, return_tree=False):
        # Render the tree
        tree = self._build_tree(self, only_named=only_named)

        for pre, fill, node in RenderTree(tree):
            if show_type:
                print(f"{pre}{node.name} ({node.type})")
            else:
                print(f"{pre}{node.name}")
        
        if return_tree: 
            return tree

  
@dataclass(kw_only=True)
class Sensor(AbstractClass):
    name: t.Optional[str] = None
    location: t.Optional[Location] = None