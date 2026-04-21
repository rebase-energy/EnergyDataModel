"""Solar assets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional, Union

import pandas as pd
import pvlib

from energydatamodel.bases import NodeAsset
from energydatamodel.element import Element


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


@dataclass(repr=False, kw_only=True)
class PVArray(NodeAsset):
    capacity: Optional[float] = None
    surface_azimuth: Optional[float] = None
    surface_tilt: Optional[float] = None
    surface_area: Optional[float] = None
    efficiency: Optional[float] = None
    module: Optional[str] = None
    module_type: str = "glass_polymer"
    module_parameters: Optional[Union[dict, pd.Series]] = None
    temperature_model_parameters: Optional[Union[dict, pd.Series]] = None


@dataclass(repr=False, kw_only=True)
class PVSystem(NodeAsset):
    """A PV system — an Asset that contains :class:`PVArray` members.

    Stored in the inherited ``members`` list. ``add_child`` enforces the type
    at runtime. The ``__post_init__`` auto-creates a single PVArray from
    top-level params if none were supplied (back-compat convenience).
    """

    capacity: Optional[float] = None
    surface_azimuth: Optional[float] = None
    surface_tilt: Optional[float] = None
    albedo: Optional[float] = None
    surface_type: Optional[str] = None
    module_parameters: Optional[dict] = None
    inverter_parameters: Optional[dict] = None
    module_type: str = "glass_polymer"
    racking_model: str = "open_rack"

    def __post_init__(self):
        # Auto-create a PVArray from top-level params if no members were supplied.
        if not self.members and all(
            v is not None for v in (self.capacity, self.surface_azimuth, self.surface_tilt)
        ):
            self.members.append(
                PVArray(
                    capacity=self.capacity,
                    surface_azimuth=self.surface_azimuth,
                    surface_tilt=self.surface_tilt,
                )
            )

    def add_child(self, obj: Element) -> None:
        if not isinstance(obj, PVArray):
            raise TypeError(
                f"PVSystem only accepts PVArray children, got {type(obj).__name__}"
            )
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

    capacity: Optional[Union[float, pd.DataFrame]] = None

    def to_geojson(self, exclude_none: bool = True):
        if self.geometry is None:
            raise ValueError("SolarPowerArea has no geometry to serialize")
        return json.loads(json.dumps(self.geometry.__geo_interface__))

    @property
    def geojson(self):
        return self.to_geojson()
