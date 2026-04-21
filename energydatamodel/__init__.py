"""energydatamodel — unified Element/Node/Edge hierarchy for energy assets & structures."""

from timedatamodel import (
    DataShape,
    DataType,
    Frequency,
    TimeSeries,
    TimeSeriesDescriptor,
    TimeSeriesType,
)
from timedatamodel import GeoLocation as TDMGeoLocation

# Core
from .element import Element
from .asset import Asset
from .node import Node
from .edge import Edge
from .reference import Reference, UnresolvedReferenceError
from .bases import GridNode, NodeAsset, Sensor

# Geospatial
from .geospatial import (
    GeoLocation,
    GeoMultiPolygon,
    GeoPolygon,
    Location,
)

# Physical assets
from .battery import Battery
from .building import Building, House
from .heatpump import HeatPump
from .hydro import HydroPowerPlant, HydroTurbine, Reservoir
from .solar import (
    FixedMount,
    PVArray,
    PVSystem,
    SingleAxisTrackerMount,
    SolarPowerArea,
)
from .weathersensor import (
    HumiditySensor,
    RadiationSensor,
    RainSensor,
    TemperatureSensor,
    WindSpeedSensor,
)
from .wind import WindFarm, WindPowerArea, WindTurbine

# Powergrid
from .powergrid import (
    Carrier,
    DeliveryPoint,
    EdgeAsset,
    Interconnection,
    JunctionPoint,
    Line,
    Link,
    Meter,
    Network,
    Pipe,
    SubNetwork,
    Transformer,
)

# Area
from .area import (
    Area,
    BiddingZone,
    ControlArea,
    Country,
    SynchronousArea,
    WeatherCell,
)

# Containers (Collection + subclasses)
from .containers import (
    Collection,
    EnergyCommunity,
    MultiSite,
    Portfolio,
    Region,
    Site,
    VirtualPowerPlant,
)

# Vocabulary
from .constructors import (
    cross_border_flow,
    electricity_demand,
    electricity_demand_area,
    electricity_supply,
    electricity_supply_area,
    gas_demand,
    gas_supply,
    grid_frequency,
    heating_demand,
    spot_price,
    temperature,
)
from .quantities import Kind, Quantity, Scope, build_metric

# JSON IO
from .json_io import (
    element_from_json,
    element_to_json,
    from_json_str,
    register_builtin_elements,
    register_element,
    register_value_type,
    to_json_str,
)

# Auto-register every Element subclass imported above for JSON dispatch.
register_builtin_elements()

# Register non-Element value dataclasses for JSON dispatch.
for _cls in (GeoLocation, GeoMultiPolygon, Carrier):
    register_value_type(_cls)
del _cls


__version__ = "0.1.0"
