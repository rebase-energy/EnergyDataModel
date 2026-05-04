"""Asset — mixin marking physical energy equipment.

``Asset`` is the umbrella for anything the energy domain treats as a physical,
commissioned piece of equipment: wind turbines, batteries, heat pumps, sensors,
meters, power lines, transformers, pipes. It is a pure mixin — never
instantiated directly and never used as a leaf type. Concrete equipment
classes inherit from ``Asset`` together with either :class:`Node` or
:class:`Edge` via the :class:`NodeAsset` / :class:`EdgeAsset` intermediates in
:mod:`energydatamodel.bases` and :mod:`energydatamodel.grid`.

``isinstance(x, Asset)`` answers "is this a piece of physical equipment?"
uniformly across node- and edge-shaped classes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from energydatamodel.element import Element, infra


@dataclass(repr=False, kw_only=True)
class Asset(Element):
    """Marker mixin for physical energy equipment.

    Carries fields genuinely shared across every piece of equipment —
    independent of whether the equipment is shaped like a graph vertex
    (``WindTurbine``) or a graph edge (``Line``).
    """

    commissioning_date: date | None = infra(default=None)
