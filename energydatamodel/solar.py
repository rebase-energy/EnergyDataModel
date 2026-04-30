"""Solar assets."""

from __future__ import annotations

import json
from dataclasses import dataclass

import pandas as pd
import pvlib

from energydatamodel.bases import NodeAsset
from energydatamodel.element import Element

__all__ = [
    "FixedMount",
    "SingleAxisTrackerMount",
    "PVArray",
    "PVSystem",
    "SolarPowerArea",
]


@dataclass
class FixedMount:
    surface_tilt: float = 0.0
    surface_azimuth: float = 0.0


@dataclass
class SingleAxisTrackerMount:
    axis_tilt: float = 0.0
    axis_azimuth: float = 0.0
    max_angle: float | tuple = 90.0
    backtrack: bool = True
    gcr: float = 0.2857142857142857
    cross_axis_tilt: float = 0.0
    racking_model: str | None = None
    module_height: float | None = None


@dataclass(repr=False, kw_only=True)
class PVArray(NodeAsset):
    capacity: float | None = None
    surface_azimuth: float | None = None
    surface_tilt: float | None = None
    surface_area: float | None = None
    efficiency: float | None = None
    module: str | None = None
    module_type: str = "glass_polymer"
    module_parameters: dict | pd.Series | None = None
    temperature_model_parameters: dict | pd.Series | None = None


@dataclass(repr=False, kw_only=True)
class PVSystem(NodeAsset):
    """A PV system — an Asset that contains :class:`PVArray` members.

    Stored in the inherited ``members`` list. ``add_child`` enforces the type
    at runtime. The ``__post_init__`` auto-creates a single PVArray from
    top-level params if none were supplied (back-compat convenience).
    """

    capacity: float | None = None
    surface_azimuth: float | None = None
    surface_tilt: float | None = None
    albedo: float | None = None
    surface_type: str | None = None
    module_parameters: dict | None = None
    inverter_parameters: dict | None = None
    module_type: str = "glass_polymer"
    racking_model: str = "open_rack"

    def __post_init__(self, lat: float | None = None, lon: float | None = None):
        super().__post_init__(lat, lon)
        # Auto-create a PVArray from top-level params if no members were supplied.
        if not self.members and all(v is not None for v in (self.capacity, self.surface_azimuth, self.surface_tilt)):
            self.members.append(
                PVArray(
                    capacity=self.capacity,
                    surface_azimuth=self.surface_azimuth,
                    surface_tilt=self.surface_tilt,
                )
            )

    def add_child(self, obj: Element) -> None:
        if not isinstance(obj, PVArray):
            raise TypeError(f"PVSystem only accepts PVArray children, got {type(obj).__name__}")
        self.members.append(obj)

    def to_pvlib(self, **kwargs):
        if self.module_parameters is None:
            self.module_parameters = {"pdc0": self.capacity}
        if "pdc0" not in self.module_parameters.keys():
            self.module_parameters["pdc0"] = self.capacity

        if self.inverter_parameters is None:
            self.inverter_parameters = {"pdc0": self.capacity}
        if "pdc0" not in self.inverter_parameters.keys():
            self.inverter_parameters["pdc0"] = self.capacity

        return pvlib.pvsystem.PVSystem(
            name=self.name,
            surface_tilt=self.surface_tilt,
            surface_azimuth=self.surface_azimuth,
            albedo=self.albedo,
            surface_type=self.surface_type,
            module_parameters=self.module_parameters,
            inverter_parameters=self.inverter_parameters,
            module_type=self.module_type,
            racking_model=self.racking_model,
            **kwargs,
        )


@dataclass(repr=False, kw_only=True)
class SolarPowerArea(NodeAsset):
    """A solar-power-potential area.

    The area's polygon lives in the inherited ``geometry`` field.
    """

    capacity: float | pd.DataFrame | None = None

    def to_geojson(self, exclude_none: bool = True):
        if self.geometry is None:
            raise ValueError("SolarPowerArea has no geometry to serialize")
        return json.loads(json.dumps(self.geometry.__geo_interface__))

    @property
    def geojson(self):
        return self.to_geojson()
