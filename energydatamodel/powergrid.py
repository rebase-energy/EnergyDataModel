from dataclasses import dataclass, field
from typing import List


@dataclass
class Carrier:
    name: str  #: The name of the energy carrier (e.g., electricity, gas).
    type: str  #: The type of the carrier (e.g., renewable, fossil).


@dataclass
class Bus:
    name: str  #: Identifier for the bus.
    carrier: Carrier  #: The carrier associated with this bus.


@dataclass
class Line:
    name: str  #: Identifier for the line.
    start_bus: Bus  #: The starting point bus of the line.
    end_bus: Bus  #: The ending point bus of the line.
    capacity: float  #: Maximum capacity of the line.


@dataclass
class Transformer:
    name: str  #: Identifier for the transformer.
    primary_bus: Bus  #: Primary side bus of the transformer.
    secondary_bus: Bus  #: Secondary side bus of the transformer.
    capacity: float  #: Maximum capacity of the transformer.


@dataclass
class Link:
    name: str  #: Identifier for the link.
    start_bus: Bus  #: The starting point bus of the link.
    end_bus: Bus  #: The ending point bus of the link.
    capacity: float  #: Maximum capacity of the link.


@dataclass
class SubNetwork:
    name: str  #: Name of the subnetwork.
    buses: List[Bus] = field(default_factory=list)  #: Buses in the subnetwork.
    lines: List[Line] = field(default_factory=list)  #: Lines in the subnetwork.


@dataclass
class Network:
    name: str  #: Name of the network.
    subnetworks: List[SubNetwork] = field(default_factory=list)  #: Subnetworks in the network.
    transformers: List[Transformer] = field(default_factory=list)  #: Transformers in the network.
    links: List[Link] = field(default_factory=list)  #: Links in the network.

