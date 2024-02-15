from dataclasses import dataclass, field
import typing as t

import energydatamodel as edm
from energydatamodel import EnergyAsset


@dataclass(repr=False)
class House(EnergyAsset):
    name: t.Optional[str] = None
    assets: t.List[EnergyAsset] = field(default_factory=list)

    def add_assets(self, assets: t.Union[EnergyAsset, t.List[EnergyAsset]]):
        if isinstance(assets, list):
            self.assets.extend(assets)
        else:
            self.assets.append(assets)

    def has_demand(self):
        return isinstance(self.timeseries, edm.TimeSeries)

    def has_pvsystem(self):
        return any(isinstance(item, edm.PVSystem) for item in self.assets)

    def has_battery(self):
        return any(isinstance(item, edm.Battery) for item in self.assets)
    
    def get_pvsystems(self):
        return [instance for instance in self.assets if isinstance(instance, edm.PVSystem)]

    def get_batteries(self):
        return [instance for instance in self.assets if isinstance(instance, edm.Battery)]