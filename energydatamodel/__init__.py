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

# Area
from .area import (
    Area,
    BiddingZone,
    ControlArea,
    Country,
    SynchronousArea,
    WeatherCell,
)
from .asset import Asset
from .bases import GridNode, NodeAsset, Sensor

# Physical assets
from .battery import Battery
from .building import Building, House

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
from .edge import Edge

# Core
from .element import Element

from .heatpump import HeatPump
from .hydro import HydroPowerPlant, HydroTurbine, Reservoir

# JSON IO
from .json_io import (
    element_from_json,
    element_to_json,
    element_to_storage_dict,
    from_json_str,
    register_builtin_elements,
    register_element,
    register_value_type,
    to_json_str,
)
from .node import Node

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
from .quantities import Kind, Quantity, Scope, build_metric
from .reference import Reference, UnresolvedReferenceError
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

# Element subclasses self-register via ``Element.__init_subclass__`` at definition
# time, so a separate walk is no longer required. Value dataclasses (non-Element)
# don't go through that hook and must still be registered explicitly.
register_value_type(Carrier)


__version__ = "0.1.0"
