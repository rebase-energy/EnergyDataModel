from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd

from energydatamodel import EnergyAsset, GeoPolygon


@dataclass
class WindTurbine(EnergyAsset):
    capacity: Union[float, pd.DataFrame]
    hub_height: Optional[float] = None
    rotor_diameter: Optional[float] = None
    turbine_model: Optional[str] = None
    power_curve: Optional[Union[pd.DataFrame, dict]] = None
    power_coefficient_curve: Optional[Union[pd.DataFrame, dict]] = None

    def create_table_representation(self):
        import ipywidgets as widgets
        # Create and return widgets to represent the WindTurbine's data
        name_label = widgets.Label('Name: ' + self.name)
        capacity_label = widgets.Label('Capacity: ' + str(self.capacity))
        # ... add more details as needed ...
        return widgets.VBox([name_label, capacity_label])

@dataclass(repr=False)
class WindFarm(EnergyAsset): 
    wind_turbines: list[WindTurbine] = None
    capacity: Union[float, pd.DataFrame] = None
    farm_efficiency: Optional[pd.DataFrame] = None

    def __post_init__(self):
        super().__post_init__()

@dataclass
class WindPowerArea:
    geopolygon: GeoPolygon 
    capacity: Union[float, pd.DataFrame]
    area: float
    wind_turbines: Optional[Union[List[WindTurbine], List[WindFarm]]] = None
    farm_efficiency: Optional[pd.DataFrame] = None