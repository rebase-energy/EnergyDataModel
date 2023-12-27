from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd
from shapely.geometry import Point
import pytz
from uuid import uuid4

from energydatamodel import Location


@dataclass(kw_only=True)
class EnergyAsset:
    name: Optional[str] = None
    location: Optional[Location] = None


@dataclass(kw_only=True)
class TimeSeries(pd.DataFrame):
    name: Optional[str] = None
    

@dataclass(kw_only=True)
class Sensor:
    name: Optional[str] = None
    location: Optional[Location] = None