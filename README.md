<div align="center">
    <img width="300" src="https://github.com/rebase-energy/EnergyDataModel/blob/main/assets/energydatamodel-logo.png?raw=true" alt="EnergyDataModel"/>
<h2 style="margin-top: 0px;">
    🔋 Represent energy systems as Python data classes for improved modularity and readability
</h2>
</div>

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/energydatamodel.svg)](https://badge.fury.io/py/energydatamodel) 
[![Join us on Slack](https://img.shields.io/badge/Join%20us%20on%20Slack-%2362BEAF?style=flat&logo=slack&logoColor=white)](https://join.slack.com/t/rebase-community/shared_invite/zt-1dtd0tdo6-sXuCEy~zPnvJw4uUe~tKeA) 
[![All Contributors](https://img.shields.io/github/all-contributors/rebase-energy/EnergyDataModel?color=ee8449&style=flat-square)](#contributors)
[![GitHub Repo stars](https://img.shields.io/github/stars/rebase-energy/EnergyDataModel?style=social)](https://github.com/rebase-energy/EnergyDataModel)

**EnergyDataModel** provides an open-source, Python-based data model that enables energy data scientists and modellers to write more modular and readable code. **EnergyDataModel** lets you: 

* 🧱 **Modularity** - Represent energy assets, energy systems and other relevant concepts as object-oriented building blocks;
* 🏗️ **Relationships** - Structure your energy assets in graphs and hierarchies representing energy systems that can be serialized to files (e.g. .csv, .json, and .geojson files);
* 👀 **Visualization** - Visualise energy systems maps, graphs, flows and structure using built-in plotting functions;
* 🤓 **Readability** - Write more explicit Python code through human-readable expressions and built-in convenience methods; 
* 🧩 **Interoperability** - Convert data format to other energy-relevant data models and ontologies; and 
* 💬 **Communicate** - Communicate effectively in teams with a common energy system data vocabulary. 

**⬇️ [Installation](#installation)**
&ensp;|&ensp;
**📖 [Documentation](https://docs.energydatamodel.org/en/latest/)**
&ensp;|&ensp;
**🚀 [Try out now in Colab](https://colab.research.google.com/github/rebase-energy/EnergyDataModel/blob/main/energydatamodel/examples/example-1-to-json.ipynb)**
&ensp;|&ensp;
**👥 [Join Community Slack](https://join.slack.com/t/rebase-community/shared_invite/zt-1dtd0tdo6-sXuCEy~zPnvJw4uUe~tKeA)**

## Modules and Data Classes
**EnergyDataModel** leverages [Python's Data Classes](https://docs.python.org/3/library/dataclasses.html) to represent energy assets as Python objects. The table below gives a summary of the available modules and data classes. 

| Module         | Data Classes     |
| :----          | :----            |
| 🗺️&nbsp;`geospatial` | [`GeoLocation`](https://docs.energydatamodel.org/en/latest/energydatamodel/geospatial.html#energydatamodel.geospatial.GeoLocation), [`GeoLine`](https://docs.energydatamodel.org/en/latest/energydatamodel/geospatial.html#energydatamodel.geospatial.GeoLine), [`GeoPolygon`](https://docs.energydatamodel.org/en/latest/energydatamodel/geospatial.html#energydatamodel.geospatial.GeoPolygon), [`GeoMultiPolygon`](https://docs.energydatamodel.org/en/latest/energydatamodel/geospatial.html#energydatamodel.geospatial.GeoMultiPolygon), [`GeoGraph`](https://docs.energydatamodel.org/en/latest/energydatamodel/geospatial.html#energydatamodel.geospatial.GeoGraph) | 
| 📈&nbsp;`timeseries` | [`ElectricityDemand`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.ElectricityDemand), [`ElectricitySupply`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.ElectricityDemand), [`HeatingDemand`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.HeatingDemand), [`HeatingSupply`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.HeatingSupply), [`ElectricityPrice`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.ElectricityPrice), [`CarbonIntensity`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.CarbonIntensity), | 
| ☀️&nbsp;`solar` | [`FixedMount`](https://docs.energydatamodel.org/en/latest/energydatamodel/solar.html#energydatamodel.solar.FixedMount), [`SingleAxisTrackerMount`](https://docs.energydatamodel.org/en/latest/energydatamodel/solar.html#energydatamodel.solar.SingleAxisTrackerMount), [`PVArray`](https://docs.energydatamodel.org/en/latest/energydatamodel/solar.html#energydatamodel.solar.PVArray), [`PVSystem`](https://docs.energydatamodel.org/en/latest/energydatamodel/solar.html#energydatamodel.solar.PVSystem), [`SolarPowerArea`](https://docs.energydatamodel.org/en/latest/energydatamodel/solar.html#energydatamodel.solar.SolarPowerArea) | 
| 🌬️&nbsp;`wind` | [`WindTurbine`](https://docs.energydatamodel.org/en/latest/energydatamodel/wind.html#energydatamodel.wind.WindTurbine), [`WindFarm`](https://docs.energydatamodel.org/en/latest/energydatamodel/wind.html#energydatamodel.wind.WindFarm), [`WindPowerArea`](https://docs.energydatamodel.org/en/latest/energydatamodel/wind.html#energydatamodel.wind.WindPowerArea) |
| 🔋&nbsp;`battery` | [`Battery`](https://docs.energydatamodel.org/en/latest/energydatamodel/battery.html#energydatamodel.battery.Battery) | 
| 💦&nbsp;`hydro` | [`Reservoir`](https://docs.energydatamodel.org/en/latest/energydatamodel/hydro.html#energydatamodel.hydro.Reservoir), [`HydroTurbine`](https://docs.energydatamodel.org/en/latest/energydatamodel/hydro.html#energydatamodel.hydro.HydroTurbine), [`HydroPowerPlant`](https://docs.energydatamodel.org/en/latest/energydatamodel/hydro.html#energydatamodel.hydro.HydroPowerPlant) |
| ♻️&nbsp;`heatpump` | [`HeatPump`](https://docs.energydatamodel.org/en/latest/energydatamodel/heatpump.html#energydatamodel.heatpump.HeatPump) |
| ⚡&nbsp;`powergrid` | [`Carrier`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Carrier), [`Bus`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Bus), [`Line`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Line), [`Transformer`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Transformer), [`Link`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Link), [`SubNetwork`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.SubNetwork), [`Network`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Network), |

Explore the data model visually [here](https://zoomhub.net/Zxa5x). \
Read the full documentation [here](https://docs.energydatamodel.org/en/latest/).

## Purpose and Philosphy
The aim of **EnergyDataModel** is to provide the energy data and modelling community with a Python-based open-source tool to enable improvement of software engineering aspects like code quality, maintainability, modularity, reusability and interoperability. We believe that bringing more rigorous software engineering practices to the energy data community has the potential to radically improve productivity, collaboration and usefulness of software tools, utimately leading to better energy decisions. 

Our philosophy is aligned on usefulness and practicality over maximizing execution performance or some kind of esoteric theoretical rigor. A well-know quote by Abelson & Sussman comes to mind: 

> **"Programs [software] are meant to be read by humans and only incidentally for computers to execute"**

Making code explicit, readable and intuitive counts. 

If you are interested in joining our mission to build open-source tools that improve productiveness and workflow of energy modellers worldwide - then [join our Slack](https://join.slack.com/t/rebase-community/shared_invite/zt-1dtd0tdo6-sXuCEy~zPnvJw4uUe~tKeA)!

## Basic usage
Create an energy system made up of two sites with co-located solar, wind and batteries and save as a .json-file. 

```python
import energydatamodel as edm

pvsystem_1 = edm.PVSystem(capacity=2400, surface_azimuth=180, surface_tilt=25)
windturbine_1 = edm.WindTurbine(capacity=3200, hub_height=120, rotor_diameter=100)
battery_1 = edm.Battery(storage_capacity=1000, min_soc=150, max_charge=500, max_discharge=500)

site_1 = edm.Site(assets=[pvsystem_1, windturbine_1, battery_1],
                  latitude=46, 
                  longitude=64)

pvsystem_2 = edm.PVSystem(capacity=2400, surface_azimuth=180, surface_tilt=25)
windturbine_2 = edm.WindTurbine(capacity=3200, hub_height=120, rotor_diameter=100)
battery_2 = edm.Battery(storage_capacity=1000, min_soc=150, max_charge=500, max_discharge=500)

site_2 = edm.Site(assets=[pvsystem_2, windturbine_2, battery_2],
                  latitude=51, 
                  longitude=58)

portfolio = edm.Portfolio(sites=[site_1, site_2])

portfolio.to_json()
```

For more examples on usage and applications of **EnergyDataModel** see the documentation examples page [here](https://docs.energydatamodel.org/en/latest/examples.html).

## Installation
Install the **stable** release: 
```bash
pip install energydatamodel
```

Install the **latest** release: 
```bash
pip install git+https://github.com/rebase-energy/EnergyDataModel
```

Install in editable mode for **development**: 
```bash
git clone https://github.com/rebase-energy/EnergyDataModel.git
cd EnergyDataModel
pip install -e . 
```

## Ways to Contribute
We welcome contributions from anyone interested in this project! Here are some ways to contribute to **EnergyDataModel**:

* Add a new energy system assets and concepts;
* Propose updates to existing energy assets and concepts; 
* Create a converter to new data format; or
* Create a converter to another energy data model.

If you are interested in contributing, then feel free to join our [Community Slack](https://join.slack.com/t/rebase-community/shared_invite/zt-1dtd0tdo6-sXuCEy~zPnvJw4uUe~tKeA) so that we can discuss it. 

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
