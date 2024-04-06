from dataclasses import dataclass, field
import typing as t
from typing import List, Optional, Union
import pandas as pd
from shapely.geometry import Point
import pytz
from uuid import uuid4

import energydatamodel as edm

#TODO
# Decide how to and production area fits in. As a time series? As a geospatial area? Or as an energy asset? 
# It is more of a time series, however, it should hold both capacity and and production data
# I want geospatial to be more of a base module
# Should it be its own separate class e.g. EnergySupply, EnergyDemand?

@dataclass
class ElectricityDemand(edm.TimeSeries):
    location: t.Optional[edm.GeoLocation] = None


ElectricityConsumption = ElectricityDemand


@dataclass
class ElectricityAreaDemand(edm.TimeSeries):
    area: t.Optional[t.Union[edm.GeoPolygon, edm.GeoMultiPolygon]] = None


ElectricityAreaConsumption = ElectricityAreaDemand


@dataclass
class ElectricitySupply(edm.TimeSeries):
    location: Optional[edm.GeoLocation] = None


ElectricityProduction = ElectricitySupply


@dataclass
class ElectricityAreaSupply(edm.TimeSeries):
    area: t.Optional[t.Union[edm.GeoPolygon, edm.GeoMultiPolygon]] = None


ElectricityAreaProduction = ElectricityAreaSupply


@dataclass
class HeatingDemand(edm.TimeSeries):
    location: Optional[edm.GeoLocation] = None


HeatingConsumption = HeatingDemand

@dataclass
class HeatingAreaDemand(edm.TimeSeries):
    area: t.Optional[t.Union[edm.GeoPolygon, edm.GeoMultiPolygon]] = None


HeatingAreaConsumption = HeatingAreaDemand


@dataclass
class HeatingSupply(edm.TimeSeries):
    location: Optional[edm.GeoLocation] = None


HeatingProduction = HeatingSupply


@dataclass
class HeatingAreaSupply(edm.TimeSeries):
    area: t.Optional[t.Union[edm.GeoPolygon, edm.GeoMultiPolygon]] = None


HeatingAreaProduction = HeatingAreaSupply


@dataclass
class ElectricityPrice(edm.TimeSeries):
    area: t.Optional[t.Union[edm.GeoPolygon, edm.GeoMultiPolygon]] = None


@dataclass
class CarbonIntensity(edm.TimeSeries):
    area: Optional[edm.GeoPolygon] = None