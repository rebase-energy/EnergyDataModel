from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd

from energydatamodel import EnergyAsset


@dataclass
class WindTurbine(EnergyAsset):
    capacity: Union[float, pd.DataFrame]
    hub_height: float
    rotor_diameter: Optional[float] = None
    turbine_model: Optional[str] = None
    power_curve: Optional[Union[pd.DataFrame, dict]] = None
    power_coefficient_curve: Optional[Union[pd.DataFrame, dict]] = None

    def __post_init__(self):
        super().__post_init__()

@dataclass
class WindFarm(EnergyAsset): 
    wind_turbines: list[WindTurbine]
    farm_efficiency: Optional[pd.DataFrame] = None

    def __post_init__(self):
        super().__post_init__()

@dataclass
class WindPowerArea: 
    capacity: Union[float, pd.DataFrame]
    area: float
    wind_turbines: Optional[Union[List[WindTurbine], List[WindFarm]]] = None
    farm_efficiency: Optional[pd.DataFrame] = None