"""Semantic intermediates under :class:`Node`.

These three subclasses don't add fields beyond what ``Node`` already gives
them (geometry inherited via ``Entity``, members + tz inherited from
``Node``); they exist as semantic markers so callers can write
``isinstance(x, Asset)`` / ``isinstance(x, GridNode)`` / ``isinstance(x, Sensor)``
to discriminate roles cleanly.

* :class:`Asset` — physical energy equipment (generates, consumes, or stores
  energy). Subclassed by WindTurbine, PVSystem, Battery, HeatPump,
  HydroPowerPlant, Building, House, etc.
* :class:`GridNode` — topological point in an electrical/grid network (a bus,
  a meter, a delivery point). Adds ``carrier``.
* :class:`Sensor` — measurement instrument. No added fields on the base;
  concrete sensor subclasses (TemperatureSensor, WindSpeedSensor, ...) carry
  installation-specific fields like ``height``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Optional

from energydatamodel.node import Node

if TYPE_CHECKING:
    from energydatamodel.powergrid import Carrier


# ---------------------------------------------------------------------
# Asset — base for physical energy equipment
# ---------------------------------------------------------------------


@dataclass(repr=False, kw_only=True)
class Asset(Node):
    """Physical energy equipment that generates, consumes, or stores energy.

    Subclasses (``WindTurbine``, ``Battery``, ``HeatPump``, ...) add their own
    domain fields. The docstring lives here; leaf classes carry only domain
    fields.
    """


# ---------------------------------------------------------------------
# GridNode — topological point in an electrical / grid network
# ---------------------------------------------------------------------


@dataclass(repr=False, kw_only=True)
class GridNode(Node):
    """A topological point in a grid network — a bus, meter, or delivery point.

    Distinct from :class:`Asset`: GridNodes don't generate or consume energy
    themselves; they're abstract points where other things connect.
    """

    carrier: Optional["Carrier"] = None

    _BASE_FIELDS: ClassVar[frozenset] = Node._BASE_FIELDS | frozenset({"carrier"})


# ---------------------------------------------------------------------
# Sensor — measurement instrument
# ---------------------------------------------------------------------


@dataclass(repr=False, kw_only=True)
class Sensor(Node):
    """A measurement instrument that observes an environmental variable.

    No fields on the base; concrete sensor subclasses (``TemperatureSensor``,
    ``WindSpeedSensor``, etc.) carry installation-specific fields like
    ``height``.
    """
