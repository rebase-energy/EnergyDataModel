===================
Quickstart Guide
===================

This quickstart guide walks you through installing EnergyDataModel and
assembling a small energy-system tree end-to-end.

Installation
------------

EnergyDataModel can be installed from PyPI:

.. code-block:: bash

   pip install energydatamodel

Python 3.12 or later is required.

Basic usage
-----------

Every structural class inherits from a single ``Element`` root. Nodes
(``WindTurbine``, ``Battery``, ...), edges (``Interconnection``, ``Line``),
and collections (``Site``, ``Portfolio``) all compose into a tree you can
serialize to JSON and reload losslessly.

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

   js = portfolio.to_json()
   restored = edm.Portfolio.from_json(js)

See the :doc:`examples` page and the ``examples/quickstart.ipynb`` notebook
for a full walkthrough including time-series descriptors, areas, edges,
cross-tree references, and geometry round-trip.
