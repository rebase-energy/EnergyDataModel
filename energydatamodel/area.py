"""Area — administrative or market-defined geographic regions.

Each area type is a proper subclass of :class:`Area` (no scope enum, no
constructor functions). Type discrimination is via ``isinstance``.

* :class:`BiddingZone` — electricity market bidding zone (e.g. SE-SE1, DE-LU)
* :class:`Country` — country-scoped area
* :class:`ControlArea` — TSO control area
* :class:`WeatherCell` — meteorological grid cell
* :class:`SynchronousArea` — AC-synchronous grid (zones sharing one frequency).
  Carries an extra ``nominal_frequency`` field (50 Hz in Europe / Nordic /
  GB / Ireland / Baltic / IPS-UPS; 60 Hz in North America).

The geometry (Polygon / MultiPolygon) lives on :class:`Element` and is
inherited; areas without a known polygon simply leave it ``None``.
"""

from dataclasses import dataclass

from energydatamodel.node import Node


@dataclass(repr=False, kw_only=True)
class Area(Node):
    """An administrative or market-defined geographic region."""


@dataclass(repr=False, kw_only=True)
class BiddingZone(Area):
    """An electricity market bidding zone (e.g. ``SE-SE1``, ``DE-LU``)."""


@dataclass(repr=False, kw_only=True)
class Country(Area):
    """A country-scoped area."""


@dataclass(repr=False, kw_only=True)
class ControlArea(Area):
    """A TSO control area."""


@dataclass(repr=False, kw_only=True)
class WeatherCell(Area):
    """A meteorological grid cell."""


@dataclass(repr=False, kw_only=True)
class SynchronousArea(Area):
    """An AC-synchronous grid — zones that share a single operating frequency.

    Examples: NSA (Nordic), CESA (Continental Europe), GBSA (Great Britain),
    ISA (Ireland), BSA (Baltic), IPSA (IPS/UPS). Default ``nominal_frequency``
    is 50.0 Hz; set 60.0 for North American synchronous areas.
    """

    nominal_frequency: float = 50.0  # Hz
