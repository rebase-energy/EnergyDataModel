Reference
=========

The ``energydatamodel`` package exposes a single :class:`~energydatamodel.Element`
root with three sibling subtrees — :class:`~energydatamodel.Node`,
:class:`~energydatamodel.Edge`, and :class:`~energydatamodel.Collection` —
plus an :class:`~energydatamodel.Asset` mixin and a small set of value
types and helpers. System-structural classes live flat at ``edm.X``;
technology-specific equipment lives under sub-namespaces (``edm.solar``,
``edm.wind``, ``edm.grid``, …).


Core hierarchy
--------------

Element
~~~~~~~

.. automodule:: energydatamodel.element
   :members:
   :show-inheritance:

Node
~~~~

.. automodule:: energydatamodel.node
   :members:
   :show-inheritance:

Edge
~~~~

.. automodule:: energydatamodel.edge
   :members:
   :show-inheritance:

Asset
~~~~~

.. automodule:: energydatamodel.asset
   :members:
   :show-inheritance:

Bases (NodeAsset, GridNode, Sensor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: energydatamodel.bases
   :members:
   :show-inheritance:


Containers
----------

Logical groupings (``Portfolio``, ``Site``, ``Region``, …) — :class:`~energydatamodel.Element`
subclasses that hold members but are not graph vertices.

.. automodule:: energydatamodel.containers
   :members:
   :show-inheritance:


Areas
-----

Administrative or market-defined geographic regions
(``BiddingZone``, ``Country``, ``ControlArea``, ``WeatherCell``, ``SynchronousArea``).

.. automodule:: energydatamodel.area
   :members:
   :show-inheritance:


☀️ Solar
--------

.. automodule:: energydatamodel.solar
   :members:
   :show-inheritance:


🌬️ Wind
--------

.. automodule:: energydatamodel.wind
   :members:
   :show-inheritance:


🔋 Battery
----------

.. automodule:: energydatamodel.battery
   :members:
   :show-inheritance:


💦 Hydro
--------

.. automodule:: energydatamodel.hydro
   :members:
   :show-inheritance:


♻️ Heat pumps
-------------

.. automodule:: energydatamodel.heatpump
   :members:
   :show-inheritance:


🏠 Buildings
------------

.. automodule:: energydatamodel.building
   :members:
   :show-inheritance:


🌡️ Weather sensors
-------------------

.. automodule:: energydatamodel.weather
   :members:
   :show-inheritance:


⚡ Power grid
-------------

Grid-topology classes — edge-equipment subclasses of :class:`~energydatamodel.grid.EdgeAsset`
(``Line``, ``Link``, ``Pipe``, ``Interconnection``), :class:`~energydatamodel.GridNode`
subclasses (``JunctionPoint``, ``Meter``, ``DeliveryPoint``, ``Transformer``),
:class:`~energydatamodel.containers.Collection` subclasses (``SubNetwork``, ``Network``),
and the plain ``Carrier`` value type.

.. automodule:: energydatamodel.grid
   :members:
   :show-inheritance:


Energy vocabulary
-----------------

Quantity / Kind / Scope enums and ``build_metric()`` for assembling dotted
metric strings like ``electricity.demand.area``.

.. automodule:: energydatamodel.quantities
   :members:
   :show-inheritance:

Convenience constructors that build metadata-only :class:`~timedatamodel.TimeSeries`
instances with pre-filled metric strings:

.. automodule:: energydatamodel.constructors
   :members:
   :show-inheritance:


References
----------

Cross-tree references — :class:`~energydatamodel.Reference`,
:class:`~energydatamodel.Index`, and :func:`~energydatamodel.build_index` —
let one :class:`~energydatamodel.Element` point at another by ``uuid``
without holding a hard Python reference. Useful for grid topology
(an :class:`~energydatamodel.Edge` referencing endpoints in a different subtree)
and for round-tripping JSON without duplicating nested objects.

.. automodule:: energydatamodel.reference
   :members:
   :show-inheritance:


JSON I/O
--------

Lossless JSON round-trip for any registered :class:`~energydatamodel.Element`
subclass. ``Element.__init_subclass__`` auto-registers subclasses, so
user-defined node/edge types serialize without any explicit decorator.
Plain value dataclasses (non-:class:`~energydatamodel.Element`) must register
themselves via :func:`~energydatamodel.register_value_type`.

.. automodule:: energydatamodel.json_io
   :members:
     element_to_json,
     element_from_json,
     element_to_storage_dict,
     to_json_str,
     from_json_str,
     register_element,
     register_value_type,
     register_builtin_elements
   :show-inheritance:
