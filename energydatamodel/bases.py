"""Node-side equipment intermediates.

* :class:`NodeAsset` — mixes ``Node`` and ``Asset``. The single mixin point on
  the node side; everything physical and vertex-shaped lives below it with
  plain single inheritance. Subclassed directly by WindTurbine, Battery,
  HeatPump, etc.; and further by :class:`Sensor` and :class:`GridNode` for
  their role-specific fields.
* :class:`Sensor` — measurement instruments. Adds ``height`` (shared by every
  concrete sensor in the weather-sensor family).
* :class:`GridNode` — topological points in an electrical / grid network
  (bus, meter, delivery point). Adds ``carrier``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from energydatamodel.asset import Asset
from energydatamodel.element import infra
from energydatamodel.node import Node

if TYPE_CHECKING:
    from energydatamodel.grid import Carrier


# ---------------------------------------------------------------------
# NodeAsset — the single (Node, Asset) mixin point
# ---------------------------------------------------------------------


@dataclass(repr=False, kw_only=True)
class NodeAsset(Node, Asset):
    """Mixin intermediate: a ``Node`` that is also an ``Asset``.

    Concrete equipment classes (``WindTurbine``, ``Battery``, ``HeatPump``, ...)
    and the role-specific intermediates :class:`Sensor` and :class:`GridNode`
    all inherit from here. Single inheritance below this point.
    """


# ---------------------------------------------------------------------
# Sensor — measurement instruments
# ---------------------------------------------------------------------


@dataclass(repr=False, kw_only=True)
class Sensor(NodeAsset):
    """A measurement instrument that observes an environmental variable.

    Concrete sensor subclasses (``TemperatureSensor``, ``WindSpeedSensor``, …)
    inherit ``height`` from here and add no new fields.
    """

    height: float | None = infra(default=None)


# ---------------------------------------------------------------------
# GridNode — topological point in a grid
# ---------------------------------------------------------------------


@dataclass(repr=False, kw_only=True)
class GridNode(NodeAsset):
    """A topological point in a grid network — a bus, meter, or delivery point.

    GridNodes are equipment too (they have manufacturers, commissioning dates,
    etc. via :class:`Asset`). They're distinguished from generation/consumption
    assets by carrying a ``carrier``.
    """

    carrier: Carrier | None = infra(default=None)
