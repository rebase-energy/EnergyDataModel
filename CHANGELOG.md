# 🚀 v0.2.0 — EnergyDataModel

EnergyDataModel is an open-source Python library for representing energy systems as plain data classes — assets, areas, grid topology, and time-series declarations — under a single `Element` root with stable UUID identity.

It gives energy engineers and energy data scientists object-oriented building blocks for portfolios, sites, and equipment that compose into trees, serialize losslessly to JSON, and round-trip into [EnergyDB](https://github.com/rebase-energy/energydb) without losing any structural state.

## 🌳 The Element Model

Everything in EnergyDataModel inherits from a single root, `Element`, which carries identity (`id: UUID`, `name`), a list of attached `TimeSeries` declarations, an optional shapely geometry, and an `extra` dict for ad-hoc JSON-scalar fields.

Three sibling subtrees specialize `Element`, plus an `Asset` mixin:

- 🟢 **`Node`** — graph vertices (equipment, areas, sensors, grid topology points). Adds `members` and `tz`.
- 🔗 **`Edge`** — directed relationships between two nodes (lines, transformers, interconnectors). Adds `from_element`, `to_element`, `directed`.
- 📦 **`Collection`** — logical groupings (Portfolio, Site, Region, …). Adds `members` and `tz`. Not a graph vertex.
- 🏷️ **`Asset`** — cross-cutting mixin marking physical equipment, mixed into Node via `NodeAsset` and into Edge via `EdgeAsset`.

System-structural classes (containers, areas, networks, bases) live flat at `edm.X`. Technology-specific equipment lives under sub-namespaces — `edm.solar.PVSystem`, `edm.wind.WindTurbine`, `edm.grid.Line`, `edm.battery.Battery`, `edm.hydro.HydroPowerPlant`, `edm.heatpump.HeatPump`, `edm.building.House`, `edm.weather.TemperatureSensor`.

## ✨ Key Features

- **UUID7 identity**: every `Element` gets a stable [UUID7](https://datatracker.ietf.org/doc/html/draft-ietf-uuidrev-rfc4122bis) at construction — survives renames, JSON round-trips, and (when paired with EnergyDB) sits as the row primary key in PostgreSQL.
- **Lossless JSON round-trip**: `element.to_json()` / `Element.from_json()` for any registered subclass. Subclasses self-register via `Element.__init_subclass__` — no decorator required.
- **User extensibility**: subclass `edm.NodeAsset` (or `edm.grid.EdgeAsset`, or `edm.Element`) and your class is auto-registered. Add ad-hoc scalar fields via the `extra: dict[str, JSONScalar]` bag without subclassing.
- **Cross-tree references**: `Reference[T]` points at another Element by UUID, resolved lazily via an `Index` (`dict[UUID, Element]` built once, O(1) lookup). JSON wire format is `{"__ref__": "<uuid>"}` — single-pass deserialize, no two-pass walk.
- **Edge endpoint widening**: `Edge.from_element` / `to_element` accept `Element | UUID | Reference` at construction; `__post_init__` normalizes everything to `Reference`.
- **GeoJSON export**: `element.to_geojson()` walks the tree and emits a `FeatureCollection` of leaves with shapely geometry.
- **Energy vocabulary**: `Quantity` / `Kind` / `Scope` enums and `build_metric()` for dotted metric strings (`electricity.demand.area`), plus convenience constructors (`electricity_supply()`, `spot_price()`, `grid_frequency()`, …) that return metadata-only `TimeSeries`.
- **Tree display & navigation**: `print(element)` / `element.to_tree()` renders the hierarchy as an indented tree; `element.children()` exposes a uniform walk across all node-bearing types.
- **Interactive class explorer**: a Cytoscape-rendered class graph (56 classes, 50 edges) is auto-rebuilt with every docs build — pan, zoom, click any class to inspect its fields and parents.

## 🛠️ Getting Started

Install via `pip`:

```bash
pip install energydatamodel
```

```python
import energydatamodel as edm
from shapely.geometry import Point

pvsystem = edm.solar.PVSystem(name="PV-1", capacity=2400, surface_azimuth=180, surface_tilt=25)
windturbine = edm.wind.WindTurbine(name="WT-1", capacity=3200, hub_height=120, rotor_diameter=100)
battery = edm.battery.Battery(name="B-1", storage_capacity=1000, max_charge=500, max_discharge=500)

site = edm.Site(name="Site-1", geometry=Point(12.8, 55.5), members=[pvsystem, windturbine, battery])
portfolio = edm.Portfolio(name="My Portfolio", members=[site])

js = portfolio.to_json()
restored = edm.Portfolio.from_json(js)
```

Try it instantly in Colab — no install needed:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rebase-energy/EnergyDataModel/blob/main/examples/quickstart.ipynb)

## 📚 Resources

- **Documentation**: <https://docs.energydatamodel.org>
- **Class explorer**: <https://docs.energydatamodel.org/en/latest/class_hierarchy.html>
- **Community**: [Join us on Slack](https://dub.sh/yTqMriJ)
- **License**: MIT

**Full Changelog**: <https://github.com/rebase-energy/EnergyDataModel/commits/v0.2.0>

Are you using EnergyDataModel in your work? We'd love to hear your feedback. Open an issue or join our Slack community to help us build a shared vocabulary for energy systems.
