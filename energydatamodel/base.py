from dataclasses import dataclass, fields
from typing import List, Optional, Union
import pandas as pd
from shapely.geometry import Point
import pytz
from uuid import uuid4

from energydatamodel import Location



@dataclass
class Base:

    def to_dataframe(self):
        """Convert data class to a pandas DataFrame."""

        data = {field.name: getattr(self, field.name) for field in fields(self)}
        df = pd.DataFrame({self.__class__.__name__: data})

        return df
    

@dataclass(kw_only=True)
class EnergyAsset(Base):
    name: Optional[str] = None
    location: Optional[Location] = None


@dataclass(kw_only=True)
class TimeSeries(pd.DataFrame):
    name: Optional[str] = None


@dataclass(kw_only=True)
class Sensor(Base):
    name: Optional[str] = None
    location: Optional[Location] = None