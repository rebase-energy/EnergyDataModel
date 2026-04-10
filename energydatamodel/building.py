from dataclasses import dataclass, field
import typing as t
from typing import ClassVar

import energydatamodel as edm
from energydatamodel import EnergyAsset


@dataclass(repr=False)
class Building(edm.EnergyAsset):
    name: t.Optional[str] = None
    type: t.Optional[str] = None
    assets: t.List[EnergyAsset] = field(default_factory=list)
    _CHILDREN_FIELDS: ClassVar[frozenset] = frozenset({"assets"})

    def children(self) -> list:
        return self.assets or []

    def add_child(self, obj) -> None:
        if isinstance(obj, EnergyAsset):
            self.assets.append(obj)
        else:
            raise TypeError(f"Building only accepts EnergyAsset children, got {type(obj).__name__}")


@dataclass(repr=False)
class House(edm.EnergyAsset):
    name: t.Optional[str] = None
    type: t.Optional[str] = None
    assets: t.List[EnergyAsset] = field(default_factory=list)
    _CHILDREN_FIELDS: ClassVar[frozenset] = frozenset({"assets"})

    def add_assets(self, assets: t.Union[EnergyAsset, t.List[EnergyAsset]]):
        if isinstance(assets, list):
            self.assets.extend(assets)
        else:
            self.assets.append(assets)

    def children(self) -> list:
        return self.assets or []

    def add_child(self, obj) -> None:
        if isinstance(obj, EnergyAsset):
            self.assets.append(obj)
        else:
            raise TypeError(f"House only accepts EnergyAsset children, got {type(obj).__name__}")

    def has_demand(self):
        return self.timeseries is not None

    def has_pvsystem(self):
        return any(isinstance(item, edm.PVSystem) for item in self.assets)

    def has_battery(self):
        return any(isinstance(item, edm.Battery) for item in self.assets)
    
    def get_pvsystems(self):
        return [instance for instance in self.assets if isinstance(instance, edm.PVSystem)]

    def get_batteries(self):
        return [instance for instance in self.assets if isinstance(instance, edm.Battery)]