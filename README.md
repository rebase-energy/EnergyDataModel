<div align="center">
    <img width="300" src="https://github.com/rebase-energy/EnergyDataModel/blob/main/assets/energydatamodel-logo.png?raw=true" alt="EnergyDataModel"/>
<h2 style="margin-top: 0px;">
    🔋 Represent energy systems as Python data classes for improved maintainability and readability
</h2>
</div>

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/energydatamodel.svg)](https://badge.fury.io/py/energydatamodel) 
[![Join us on Slack](https://img.shields.io/badge/Join%20us%20on%20Slack-%2362BEAF?style=flat&logo=slack&logoColor=white)](https://join.slack.com/t/rebase-community/shared_invite/zt-1dtd0tdo6-sXuCEy~zPnvJw4uUe~tKeA) 
[![GitHub Repo stars](https://img.shields.io/github/stars/rebase-energy/EnergyDataModel?style=social)](https://github.com/rebase-energy/EnergyDataModel)

## TL;DR
The `energydatamodel` let's you: 

* Create `python` data classes representing energy assets and relevant concepts;
* Structure your energy assets in graphs and hierarchies representing energy systems that can be seralised to files (e.g. .csv, .json, .geojson);
* Convert data format to other energy-relevant data models and ontologies.
* Visualise energy systems maps, graphs and flows using built-in plotting functions;
* Write `python` code with more human-readable expressions using built-in convenience methods;
* Communicate effectively with a common energy system vocabulary; and

## Modules and Data Classes
`energydatamodel` leverages [Python's Data Classes](https://docs.python.org/3/library/dataclasses.html) to represent energy assets as Python objects. The table below gives a summary of the available modules and data classes. 

| Module         | Data Classes     |
| :----          | :----       |
| 🗺️&nbsp;`geospatial` | [`GeoLocation`](https://docs.energydatamodel.org/en/latest/energydatamodel/geospatial.html#energydatamodel.geospatial.GeoLocation), [`GeoLine`](https://docs.energydatamodel.org/en/latest/energydatamodel/geospatial.html#energydatamodel.geospatial.GeoLine), [`GeoPolygon`](https://docs.energydatamodel.org/en/latest/energydatamodel/geospatial.html#energydatamodel.geospatial.GeoPolygon), [`GeoMultiPolygon`](https://docs.energydatamodel.org/en/latest/energydatamodel/geospatial.html#energydatamodel.geospatial.GeoMultiPolygon), [`GeoGraph`](https://docs.energydatamodel.org/en/latest/energydatamodel/geospatial.html#energydatamodel.geospatial.GeoGraph) | 
| 📈&nbsp;`timeseries` | [`ElectricityDemand`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.ElectricityDemand), [`ElectricitySupply`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.ElectricityDemand), [`HeatingDemand`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.HeatingDemand), [`HeatingSupply`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.HeatingSupply), [`ElectricityPrice`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.ElectricityPrice), [`CarbonIntensity`](https://docs.energydatamodel.org/en/latest/energydatamodel/timeseries.html#energydatamodel.timeseries.CarbonIntensity), | 
| ☀️&nbsp;`solar` | [`FixedMount`](https://docs.energydatamodel.org/en/latest/energydatamodel/solar.html#energydatamodel.solar.FixedMount), [`SingleAxisTrackerMount`](https://docs.energydatamodel.org/en/latest/energydatamodel/solar.html#energydatamodel.solar.SingleAxisTrackerMount), [`PVArray`](https://docs.energydatamodel.org/en/latest/energydatamodel/solar.html#energydatamodel.solar.PVArray), [`PVSystem`](https://docs.energydatamodel.org/en/latest/energydatamodel/solar.html#energydatamodel.solar.PVSystem), [`SolarPowerArea`](https://docs.energydatamodel.org/en/latest/energydatamodel/solar.html#energydatamodel.solar.SolarPowerArea) | 
| 🌬️&nbsp;`wind` | [`WindTurbine`](https://docs.energydatamodel.org/en/latest/energydatamodel/wind.html#energydatamodel.wind.WindTurbine), [`WindFarm`](https://docs.energydatamodel.org/en/latest/energydatamodel/wind.html#energydatamodel.wind.WindFarm), [`WindPowerArea`](https://docs.energydatamodel.org/en/latest/energydatamodel/wind.html#energydatamodel.wind.WindPowerArea) |
| 🔋&nbsp;`battery` | [website](https://www.pandapower.org/) | 
| 💦&nbsp;`hydro` | [`Reservoir`](https://docs.energydatamodel.org/en/latest/energydatamodel/hydro.html#energydatamodel.hydro.Reservoir), [`HydroTurbine`](https://docs.energydatamodel.org/en/latest/energydatamodel/hydro.html#energydatamodel.hydro.HydroTurbine), [`HydroPowerPlant`](https://docs.energydatamodel.org/en/latest/energydatamodel/hydro.html#energydatamodel.hydro.HydroPowerPlant) |
| ♻️&nbsp;`heatpump` | [`HeatPump`](https://docs.energydatamodel.org/en/latest/energydatamodel/heatpump.html#energydatamodel.heatpump.HeatPump) |
| ⚡&nbsp;`powergrid` | [`Carrier`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Carrier), [`Bus`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Bus), [`Line`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Line), [`Transformer`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Transformer), [`Link`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Link), [`SubNetwork`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.SubNetwork), [`Network`](https://docs.energydatamodel.org/en/latest/energydatamodel/powergrid.html#energydatamodel.powergrid.Network), |

## Purpose and philosphy
The ultimate goal of `energydatamodel` is to enable the energy data and modelling community with a `python`-based tool to improve code quality, modularity and collaboration. We believe that bringing rigorous software engineering practices to the energy community has the potential to radically improve productivity and usefulness of software tools. 

Project philosophy: 

- Making code explicit, readable and intuitive counts. “Programs are meant to be read by humans and only incidentally for computers to execute”. 

- Occam’s Razor / Keep It Simple, Stupid (KISS): the best solution is usually also the simplest one. Over-engineering is the root of all evil. 

- A data model is a standard and standards are only useful if they make your life easier. Start with the end outcome in mind. 

If you are interested in joining our mission to improve the lifes and productiveness of energy modellers world-wide - then [join our slack](https://join.slack.com/t/rebase-community/shared_invite/zt-1dtd0tdo6-sXuCEy~zPnvJw4uUe~tKeA)!

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

### Basic usage

Create an energy system made up of two sites with co-located solar, wind and batteries and save as a .json. 

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

energysystem = edm.EnergySystem(sites=[site_1, site_2])

energysystem.save_json('my_energysystem.json')
```

For more examples on usage and applications for `energydatamodel` see the documentation page [here](https://docs.energydatamodel.org/en/latest/).

### Feature #2: use `python` data classes to organise 


## Converters
`energydatamodel` provides converters to and from other popular data models and ontologies. Below is a summary of the available converters: 

| Project name   | Links     | Converter to  | Converter from  |
| :---           | :----       | :----         | :----           |
| `pvlib`        | [code](https://github.com/pvlib/pvlib-python) | ✅ | ✅ |
| `Windpowerlib` | [docs](https://windpowerlib.readthedocs.io/en/stable/) | ✅ | ✅ |
| `PyCity` | [code](https://github.com/RWTH-EBC/pyCity) | ✅ | ✅ |
| `PyPSA` | [website](https://pypsa.org/) | ✅ | ✅ |
| `Pandapower` | [website](https://www.pandapower.org/) |  | ✅ |

## Relation to rebase.energy
[rebase.energy](https://www.rebase.energy/) is the company behind `energydatamodel`. The idea behind the project stems from many hard-won lessons on how to improve working with energy-relevant data and is used extensively within rebase.energy today. `energydatamodel` is developed outside of rebase.energy's commercial offering. It is provided under the permissive MIT-licence (see licence [here](https://github.com/rebase-energy/EnergyDataModel/blob/main/LICENCE.md)) and will always be free-to-use for any purpose (including commercial). 


[![Class Structure](https://github.com/rebase-energy/EnergyDataModel/blob/main/assets/classes_energydatamodel.png?raw=true)](https://zoomhub.net/Zxa5x)