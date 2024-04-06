import dataclasses
from dataclasses import dataclass, field, fields
import typing as t
import pandas as pd
import matplotlib.pyplot as plt
import shapely
from shapely.geometry import mapping, Point, Polygon, LineString
import pytz
from uuid import uuid4

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
class EnergySystem(AbstractClass):
    """EnergySystem base class."""

    name: t.Optional[str] = None

@dataclass(kw_only=True)
class Sensor(AbstractClass):
    name: t.Optional[str] = None
    location: t.Optional[Location] = None