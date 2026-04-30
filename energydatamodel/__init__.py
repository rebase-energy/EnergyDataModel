"""energydatamodel — unified Element/Node/Edge hierarchy for energy assets & structures.

System-structural classes (containers, areas, networks, bases, utilities) are
exposed flat at ``edm.X``. Technology-specific equipment lives under
sub-namespaces:

* ``edm.solar`` — PV systems, arrays, mounts, solar areas
* ``edm.wind`` — turbines, farms, wind areas
* ``edm.battery`` — Battery
* ``edm.hydro`` — reservoirs, turbines, plants
* ``edm.heatpump`` — HeatPump
* ``edm.building`` — Building, House
* ``edm.weather`` — temperature/wind/radiation/rain/humidity sensors
* ``edm.grid`` — Carrier, edges (Line, Link, Pipe, Interconnection),
  grid nodes (JunctionPoint, Meter, DeliveryPoint, Transformer),
  Network/SubNetwork, EdgeAsset

Subclassing any registered Element class (e.g. ``edm.NodeAsset``,
``edm.grid.EdgeAsset``) auto-registers the subclass for JSON round-trips —
no decorator required. See the README for the extension recipe.
"""

from timedatamodel import (
    DataShape,
    DataType,
    Frequency,
    TimeSeries,
    TimeSeriesDescriptor,
    TimeSeriesType,
)
from timedatamodel import GeoLocation as TDMGeoLocation

# Sub-namespaces — tech-specific equipment.
from . import battery, building, grid, heatpump, hydro, solar, weather, wind

# Areas
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
from .grid import Carrier

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
from .quantities import Kind, Quantity, Scope, build_metric
from .reference import Reference, UnresolvedReferenceError

# Element subclasses self-register via ``Element.__init_subclass__`` at definition
# time, so a separate walk is no longer required. Value dataclasses (non-Element)
# don't go through that hook and must still be registered explicitly.
register_value_type(Carrier)


__all__ = [
    # Core / bases
    "Element",
    "Node",
    "Edge",
    "Asset",
    "NodeAsset",
    "Sensor",
    "GridNode",
    # Containers
    "Collection",
    "Site",
    "MultiSite",
    "Portfolio",
    "Region",
    "EnergyCommunity",
    "VirtualPowerPlant",
    # Areas
    "Area",
    "BiddingZone",
    "Country",
    "ControlArea",
    "WeatherCell",
    "SynchronousArea",
    # Reference
    "Reference",
    "UnresolvedReferenceError",
    # Quantities
    "Quantity",
    "Scope",
    "Kind",
    "build_metric",
    # JSON I/O
    "element_from_json",
    "element_to_json",
    "element_to_storage_dict",
    "from_json_str",
    "to_json_str",
    "register_element",
    "register_value_type",
    "register_builtin_elements",
    # Constructors
    "electricity_supply",
    "electricity_demand",
    "electricity_supply_area",
    "electricity_demand_area",
    "spot_price",
    "cross_border_flow",
    "grid_frequency",
    "temperature",
    "gas_supply",
    "gas_demand",
    "heating_demand",
    # timedatamodel re-exports
    "DataShape",
    "DataType",
    "Frequency",
    "TimeSeries",
    "TimeSeriesDescriptor",
    "TimeSeriesType",
    "TDMGeoLocation",
    # Sub-namespaces
    "solar",
    "wind",
    "battery",
    "hydro",
    "heatpump",
    "building",
    "weather",
    "grid",
]


__version__ = "0.1.0"
