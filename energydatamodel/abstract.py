from dataclasses import dataclass, field, fields
import typing as t
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from shapely.geometry import Point
import pytz
from uuid import uuid4

import energydatamodel as edm
from energydatamodel import BaseClass, Location


@dataclass(repr=False, kw_only=True)
class TimeSeries(BaseClass):
    name: t.Optional[str] = None
    df: t.Optional[pd.DataFrame] = None
    column_name: t.Optional[t.Union[str, int, t.Tuple[str], t.Tuple[int]]] = None

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
class EnergyAsset(BaseClass):
    """Get data from :class: `TimeSeries`"""

    name: t.Optional[str] = None
    location: t.Optional[Location] = None
    longitude: t.Optional[float] = None
    latitude: t.Optional[float] = None
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
            del self.longitude
            del self.latitude
            del self.altitude
            del self.tz
    
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


@dataclass(kw_only=True)
class Sensor(BaseClass):
    name: t.Optional[str] = None
    location: t.Optional[Location] = None