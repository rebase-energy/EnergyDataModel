from dataclasses import dataclass, field
from typing import List, Optional
import pytz


@dataclass
class Site:
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    tz: Optional[pytz.timezone] = None


@dataclass
class EnergyAsset:
    id: int
    name: str
    location: str


@dataclass
class PVModule(EnergyAsset):
    capacity: Optional[float] = None 
    efficiency: Optional[float] = None  # Efficiency in percentage
    area: Optional[float] = None        # Area in square meters


@dataclass
class EnergySystem:
    assets: List[EnergyAsset] = field(default_factory=list)

    def add_asset(self, asset: EnergyAsset):
        self.assets.append(asset)

    def remove_asset(self, asset_id: int):
        self.assets = [asset for asset in self.assets if asset.id != asset_id]

    def __str__(self):
        asset_details = '\n'.join(str(asset) for asset in self.assets)
        return f"EnergySystem with assets:\n{asset_details}"


# Example Usage
if __name__ == "__main__":
    # Create some energy assets
    solar_panel = PVModule(id=1, name="Solar Panel", capacity=100, location="Rooftop")
    #wind_turbine = EnergyAsset(id=2, name="Wind Turbine", capacity=200, location="Hillside")

    # Create an energy system and add assets to it
    energy_system = EnergySystem()
    energy_system.add_asset(solar_panel)
    #energy_system.add_asset(wind_turbine)

    # Display the energy system
    print(energy_system)
    #print(f"Total Capacity: {energy_system.total_capacity()} kW")
