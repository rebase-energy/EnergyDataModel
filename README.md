<div align="center">
    <img height="80" src="https://github.com/rebase-energy/EnergyDataModel/blob/main/assets/logo-energydatamodel.png?raw=true" alt="EnergyDataModel"/>
<h2 style="margin-top: 0px;">
    🔋 Represent energy systems as Python data classes for improved modularity and readability
</h2>
</div>

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg">
  </a>
  <a href="https://pypi.org/project/energydatamodel/">
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/energydatamodel.svg?color=blue">
  </a>
  <a href="https://dub.sh/yTqMriJ">
    <img alt="Join us on Slack" src="https://img.shields.io/badge/Join%20us%20on%20Slack-%234A154B?style=flat&logo=slack&logoColor=white">
  </a>
  <a href="#contributors">
    <img alt="All Contributors" src="https://img.shields.io/github/all-contributors/rebase-energy/EnergyDataModel?color=2b2292&style=flat-square">
  </a>
  <a href="https://github.com/rebase-energy/EnergyDataModel">
    <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/rebase-energy/EnergyDataModel?style=social">
  </a>
</p>

**EnergyDataModel** provides an open-source, Python-based data model that enables energy data scientists and modellers to write more modular and readable code. **EnergyDataModel** lets you: 

* 🧱 **Modularity** - Represent energy assets, energy systems and other relevant concepts as object-oriented building blocks;
* 🏗️ **Relationships** - Structure your energy assets in graphs and hierarchies representing energy systems that can be serialized to files (e.g. .csv, .json, and .geojson files);
* 🤓 **Readability** - Write more explicit Python code through human-readable expressions and built-in convenience methods; 
* 🧩 **Interoperability** - Convert data format to other energy-relevant data models and ontologies; and 
* 💬 **Communicate** - Communicate effectively in teams with a common energy system data vocabulary. 

**⬇️ [Installation](#installation)**
&ensp;|&ensp;
**📖 [Documentation](https://docs.energydatamodel.org/en/latest/)**
&ensp;|&ensp;
**🚀 [Try out now in Colab](https://colab.research.google.com/github/rebase-energy/EnergyDataModel/blob/main/energydatamodel/examples/example-1-to-tree-json.ipynb)**
&ensp;|&ensp;
**👋 [Join Slack Community](https://dub.sh/yTqMriJ)**

## Class hierarchy

Everything in EnergyDataModel inherits from a single root, `Entity`, which carries identity (`name`, `_id`), attached time-series descriptors, and an optional [shapely](https://shapely.readthedocs.io/) geometry. Two sibling subtrees specialize it:

* **`Node`** — anything that exists as a thing (assets, areas, sensors, grid nodes, collections). Adds `members` and `tz`.
* **`Edge`** — relationships between two nodes (lines, transformers, interconnectors). Adds `from_entity`, `to_entity`, `directed`.

```
Entity  (name, _id, timeseries, geometry)
├── Node  (+ members, tz)
│   ├── Asset                — physical energy equipment
│   │   WindTurbine, WindFarm, WindPowerArea, PVArray, PVSystem,
│   │   SolarPowerArea, Battery, HeatPump, HydroPowerPlant,
│   │   HydroTurbine, Reservoir, Building, House
│   ├── GridNode             — topological grid points (carrier)
│   │   JunctionPoint, Meter, DeliveryPoint
│   ├── Sensor               — measurement instruments
│   │   TemperatureSensor, WindSpeedSensor, RadiationSensor,
│   │   RainSensor, HumiditySensor
│   ├── Area                 — administrative / market regions
│   │   BiddingZone, Country, ControlArea, WeatherCell,
│   │   SynchronousArea (+ nominal_frequency)
│   └── Collection           — grouping / container marker
│       Portfolio, Site, MultiSite, Region,
│       EnergyCommunity, VirtualPowerPlant, SubNetwork, Network
└── Edge  (+ from_entity, to_entity, directed)
    Line, Link, Transformer, Pipe, Interconnection
```

| Module         | Data Classes |
| :----          | :----        |
| 🧱&nbsp;`entity` / `node` / `edge` | `Entity`, `Node`, `Edge` |
| 🏷️&nbsp;`bases` | `Asset`, `GridNode`, `Sensor` |
| 🗺️&nbsp;`geospatial` | `GeoLocation`, `GeoPolygon`, `GeoMultiPolygon` |
| ☀️&nbsp;`solar` | `FixedMount`, `SingleAxisTrackerMount`, `PVArray`, `PVSystem`, `SolarPowerArea` |
| 🌬️&nbsp;`wind` | `WindTurbine`, `WindFarm`, `WindPowerArea` |
| 🔋&nbsp;`battery` | `Battery` |
| 💦&nbsp;`hydro` | `Reservoir`, `HydroTurbine`, `HydroPowerPlant` |
| ♻️&nbsp;`heatpump` | `HeatPump` |
| 🏠&nbsp;`building` | `Building`, `House` |
| 🌡️&nbsp;`weathersensor` | `TemperatureSensor`, `WindSpeedSensor`, `RadiationSensor`, `RainSensor`, `HumiditySensor` |
| ⚡&nbsp;`powergrid` | `Carrier`, `JunctionPoint`, `Meter`, `DeliveryPoint`, `Line`, `Link`, `Transformer`, `Pipe`, `Interconnection`, `SubNetwork`, `Network` |
| 🗺️&nbsp;`area` | `Area`, `BiddingZone`, `Country`, `ControlArea`, `WeatherCell`, `SynchronousArea` |
| 📦&nbsp;`containers` | `Collection`, `Portfolio`, `Site`, `MultiSite`, `Region`, `EnergyCommunity`, `VirtualPowerPlant` |
| 📈&nbsp;`constructors` | `electricity_supply`, `electricity_demand`, `electricity_supply_area`, `electricity_demand_area`, `spot_price`, `cross_border_flow`, `grid_frequency`, `temperature`, `gas_supply`, `gas_demand`, `heating_demand` |

Explore the data model visually [here](https://zoomhub.net/Zxa5x). \
Read the full documentation [here](https://docs.energydatamodel.org/en/latest/).

## Purpose and Philosphy
The aim of **EnergyDataModel** is to provide the energy data and modelling community with a Python-based open-source tool to enable improvement of software engineering aspects like code quality, maintainability, modularity, reusability and interoperability. We believe that bringing more rigorous software engineering practices to the energy data community has the potential to radically improve productivity, collaboration and usefulness of software tools, utimately leading to better energy decisions. 

Our philosophy is aligned on usefulness and practicality over maximizing execution performance or some kind of esoteric theoretical rigor. A well-know quote by Abelson & Sussman comes to mind: 

> **"Programs [software] are meant to be read by humans and only incidentally for computers to execute"**

Making code explicit, readable and intuitive counts. 

If you are interested in joining our mission to build open-source tools that improve productiveness and workflow of energy modellers worldwide - then [join our Slack](https://dub.sh/yTqMriJ)!

## Basic usage
Create an energy system made up of two sites with co-located solar, wind and batteries and save as a JSON-file.

```python
import energydatamodel as edm
from shapely.geometry import Point

pvsystem_1 = edm.PVSystem(name="PV-1", capacity=2400, surface_azimuth=180, surface_tilt=25)
windturbine_1 = edm.WindTurbine(name="WT-1", capacity=3200, hub_height=120, rotor_diameter=100)
battery_1 = edm.Battery(name="B-1", storage_capacity=1000, min_soc=150, max_charge=500, max_discharge=500)

site_1 = edm.Site(name="Site-1",
                  geometry=Point(64, 46),  # (lon, lat)
                  members=[pvsystem_1, windturbine_1, battery_1])

pvsystem_2 = edm.PVSystem(name="PV-2", capacity=2400, surface_azimuth=180, surface_tilt=25)
windturbine_2 = edm.WindTurbine(name="WT-2", capacity=3200, hub_height=120, rotor_diameter=100)
battery_2 = edm.Battery(name="B-2", storage_capacity=1000, min_soc=150, max_charge=500, max_discharge=500)

site_2 = edm.Site(name="Site-2",
                  geometry=Point(58, 51),
                  members=[pvsystem_2, windturbine_2, battery_2])

portfolio = edm.Portfolio(name="My Portfolio", members=[site_1, site_2])

portfolio.to_json()
```

### Modeling a synchronous area with grid frequency

```python
import energydatamodel as edm

nsa = edm.SynchronousArea(
    name="NSA",
    nominal_frequency=50.0,
    members=[
        edm.BiddingZone(name="SE-SE1"),
        edm.BiddingZone(name="SE-SE2"),
        edm.BiddingZone(name="NO1"),
        edm.BiddingZone(name="FI"),
    ],
    timeseries=[edm.grid_frequency()],
)
```

For more examples on usage and applications of **EnergyDataModel** see the documentation examples page [here](https://docs.energydatamodel.org/en/latest/examples.html).

## Installation
We recommend installing using a virtual environment like [venv](https://docs.python.org/3/library/venv.html), [poetry](https://python-poetry.org/) or [uv](https://docs.astral.sh/uv/). 

Install the **stable** release: 
```bash
pip install energydatamodel
```

Install the **latest** release: 
```bash
pip install git+https://github.com/rebase-energy/EnergyDataModel.git
```

Install in editable mode for **development**: 
```bash
git clone https://github.com/rebase-energy/EnergyDataModel.git
cd EnergyDataModel
pip install -e .[dev] 
```

## Ways to Contribute
We welcome contributions from anyone interested in this project! Here are some ways to contribute to **EnergyDataModel**:

* Add a new energy system assets and concepts;
* Propose updates to existing energy assets and concepts; 
* Create a converter to new data format; or
* Create a converter to another energy data model.

If you are interested in contributing, then feel free to join our [Slack Community](https://dub.sh/yTqMriJ) so that we can discuss it. 👋

## Contributors
This project uses [allcontributors.org](https://allcontributors.org/) to recognize all contributors, including those that don't push code. 

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/sebaheg"><img src="https://avatars.githubusercontent.com/u/26311427?v=4?s=100" width="100px;" alt="Sebastian Haglund"/><br /><sub><b>Sebastian Haglund</b></sub></a><br /><a href="#code-sebaheg" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/nelson-sommerfeldt"><img src="https://avatars.githubusercontent.com/u/95913116?v=4?s=100" width="100px;" alt="Nelson"/><br /><sub><b>Nelson</b></sub></a><br /><a href="#ideas-nelson-sommerfeldt" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Licence
This project uses the [MIT Licence](LICENCE.md).  

## Acknowledgement
The authors of this project would like to thank the Swedish Energy Agency for their financial support under the E2B2 program (project number P2022-00903)