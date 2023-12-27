from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd
from shapely.geometry import Point
import pytz
from uuid import uuid4

from energydatamodel import Sensor


@dataclass
class TemperatureSensor(Sensor):
    height: Optional[float] = None


@dataclass
class WindSpeedSensor(Sensor):
    height: Optional[float] = None


@dataclass
class RadiationSensor(Sensor):
    height: Optional[float] = None


@dataclass
class RainSensor(Sensor):
    height: Optional[float] = None


@dataclass
class HumiditySensor(Sensor):
    height: Optional[float] = None