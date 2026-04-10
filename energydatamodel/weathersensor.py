"""Weather sensors — concrete :class:`Sensor` subclasses observing
environmental variables."""

from dataclasses import dataclass
from typing import Optional

from energydatamodel.bases import Sensor


@dataclass(repr=False, kw_only=True)
class TemperatureSensor(Sensor):
    height: Optional[float] = None


@dataclass(repr=False, kw_only=True)
class WindSpeedSensor(Sensor):
    height: Optional[float] = None


@dataclass(repr=False, kw_only=True)
class RadiationSensor(Sensor):
    height: Optional[float] = None


@dataclass(repr=False, kw_only=True)
class RainSensor(Sensor):
    height: Optional[float] = None


@dataclass(repr=False, kw_only=True)
class HumiditySensor(Sensor):
    height: Optional[float] = None
