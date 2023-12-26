from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd
from shapely.geometry import Point
import pytz
from uuid import uuid4



@dataclass
class Reservoir:
    """
    Models a reservoir used in a hydroelectric power plant for storing water.

    """
    capacity: float  #: The total water capacity of the reservoir in cubic meters.
    surface_area: float  #: The surface area of the reservoir in square kilometers.
    average_depth: float  #: The average depth of the reservoir in meters.
    location: str  #: The geographical location of the reservoir.


@dataclass(kw_only=True)
class HydroTurbine:
    """
    Represents an individual hydro turbine in a hydroelectric power plant.

    Attributes:
        turbine_type (str): The type of the hydro turbine (e.g. Francis, Kaplan).
        capacity (float): The maximum power output capacity of the turbine in megawatts (MW).
        efficiency (float): The efficiency of the turbine as a percentage.
        operational_since (Optional[int]): The year when the turbine became operational. Defaults to None.
    """
    turbine_type: str
    capacity: float
    efficiency: float
    operational_since: Optional[int] = None



@dataclass
class HydroPowerPlant:
    capacity: float  # in megawatts (MW)
    location: str  # Geographical location
    river: str  # Name of the river or water body
    annual_output: float  # Annual energy output in MWh
    turbine_type: str  # Type of turbine used (e.g., Francis, Kaplan)
    reservoir_capacity: Optional[float] = None  # Capacity of the reservoir in cubic meters, if applicable
    operational_since: Optional[int] = None  # Year when the plant became operational
    environmental_impact: Optional[str] = None  # Description of any environmental impacts
    maintenance_schedule: Optional[Union[pd.DataFrame, dict]] = None  # Maintenance schedule data, if available