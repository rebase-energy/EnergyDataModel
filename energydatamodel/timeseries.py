from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd
from shapely.geometry import Point
import pytz
from uuid import uuid4

import energydatamodel as edm


@dataclass
class ElectricityDemand(edm.TimeSeries):
    location: Optional[edm.Location] = None


@dataclass
class ElectricityAreaDemand(edm.TimeSeries):
    area: Optional[edm.Polygon] = None


@dataclass
class ElectricityProduction(edm.TimeSeries):
    location: Optional[edm.Location] = None


@dataclass
class ElectricityAreaProduction(edm.TimeSeries):
    area: Optional[edm.Polygon] = None


@dataclass
class HeatingDemand(edm.TimeSeries):
    location: Optional[edm.Location] = None


@dataclass
class HeatingAreaDemand(edm.TimeSeries):
    area: Optional[edm.Polygon] = None


@dataclass
class HeatingProduction(edm.TimeSeries):
    location: Optional[edm.Location] = None


@dataclass
class HeatingAreaProduction(edm.TimeSeries):
    area: Optional[edm.Polygon] = None

@dataclass
class EnergyPrices(edm.TimeSeries):
    area: Optional[edm.Polygon] = None


@dataclass
class CarbonIntensity(edm.TimeSeries):
    area: Optional[edm.Polygon] = None