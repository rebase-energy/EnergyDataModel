.. energydatamodel documentation master file

Welcome to EnergyDataModel
==========================

**EnergyDataModel** is an open-source Python library that represents energy systems as plain Python data classes — assets, areas, grid topology, and time-series declarations — under a single :class:`~energydatamodel.Element` root with stable UUID identity.


What is EnergyDataModel?
------------------------

Every structural class in EnergyDataModel inherits from a single root, :class:`~energydatamodel.Element`, which carries identity (``id: UUID``, ``name``), a list of attached :class:`~timedatamodel.TimeSeries` declarations, an optional `shapely <https://shapely.readthedocs.io/>`_ geometry, and an ``extra`` dict for ad-hoc JSON-scalar fields. Identity is a `UUID7 <https://datatracker.ietf.org/doc/html/draft-ietf-uuidrev-rfc4122bis>`_ generated at construction time — stable across renames, round-trips through JSON, and (when paired with `EnergyDB <https://github.com/rebase-energy/energydb>`_) usable as the row primary key in PostgreSQL.

Three sibling subtrees specialize :class:`~energydatamodel.Element`, plus an :class:`~energydatamodel.Asset` mixin:

- 🟢 :class:`~energydatamodel.Node` — graph vertices (equipment, areas, sensors, grid topology points). Adds ``members`` and ``tz``.
- 🔗 :class:`~energydatamodel.Edge` — relationships between two nodes (lines, transformers, interconnectors). Adds ``from_element``, ``to_element``, ``directed``.
- 📦 :class:`~energydatamodel.Collection` — logical groupings (Portfolio, Site, …). Adds ``members`` and ``tz``. Not a graph vertex.
- 🏷️ :class:`~energydatamodel.Asset` — cross-cutting mixin marking physical equipment. Mixed into Node via :class:`~energydatamodel.NodeAsset` and into Edge via :class:`~energydatamodel.grid.EdgeAsset`.


Why EnergyDataModel?
--------------------

EnergyDataModel lets energy modellers and data scientists trade ad-hoc dicts for typed objects without leaving Python:

- 🧱 **Modularity** — represent assets, systems, and concepts as object-oriented building blocks.
- 🏗️ **Relationships** — structure assets as graphs and hierarchies that serialize losslessly to JSON / GeoJSON.
- 🤓 **Readability** — write explicit Python through human-readable expressions and convenience methods.
- 🧩 **Interoperability** — convert to other energy data models, ontologies, and formats.
- 💬 **Communicate** — share a common vocabulary across teams.


Quick Start
-----------

.. code-block:: bash

   pip install energydatamodel

.. code-block:: python

   import energydatamodel as edm
   from shapely.geometry import Point

   pvsystem = edm.solar.PVSystem(name="PV-1", capacity=2400, surface_azimuth=180, surface_tilt=25)
   windturbine = edm.wind.WindTurbine(name="WT-1", capacity=3200, hub_height=120, rotor_diameter=100)
   battery = edm.battery.Battery(name="B-1", storage_capacity=1000, max_charge=500, max_discharge=500)

   site = edm.Site(
       name="Site-1",
       geometry=Point(12.8, 55.5),  # (lon, lat)
       members=[pvsystem, windturbine, battery],
   )

   portfolio = edm.Portfolio(name="My Portfolio", members=[site])

   # Lossless JSON round-trip
   js = portfolio.to_json()
   restored = edm.Portfolio.from_json(js)


Release Notes
-------------

For version-by-version changes, see:

- `Changelog <https://github.com/rebase-energy/EnergyDataModel/blob/main/CHANGELOG.md>`_


Documentation
-------------

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   installation
   quickstart
   class_hierarchy
   reference
   examples


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
