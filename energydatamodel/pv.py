from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd
from shapely.geometry import Point
import pytz
from uuid import uuid4

from energydatamodel import EnergyAsset


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