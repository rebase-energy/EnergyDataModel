from dataclasses import dataclass
from typing import Optional, Union
import pandas as pd

@dataclass
class HeatPump:
    """
    Represents a heat pump in an energy system.
    """

    capacity: float  #: The heating or cooling capacity of the heat pump in kilowatts (kW).
    cop: float  #: Coefficient of Performance - the ratio of heating or cooling provided to electrical energy consumed.
    energy_source: str  #: The primary energy source used, e.g., 'electricity', 'geothermal'.