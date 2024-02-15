# EnergyDataModel

[![Join us on Slack](https://img.shields.io/badge/Join%20us%20on%20Slack-%2362BEAF?style=flat&logo=slack&logoColor=white)]
(https://join.slack.com/t/rebase-community/shared_invite/zt-1dtd0tdo6-sXuCEy~zPnvJw4uUe~tKeA)

## TL;DR;

The `energydatamodel` let's you: 

* Create `python` objects representing energy assets and relevant concepts
* Structure your energy assets in graphs and hierarchies representing energy systems
* Structure energy asset data in `python` dataclasses that can be seralised to files (e.g. .csv, .json, .geojson)
* Visualise energy systems using built-in plotting functions
* Convert data to other energy-relevant data models and ontologies

## Purpose and philosphy
The ultimate goal of `energydatamodel` is to enable the energy data and modelling community with a `python`-based tool to improve code quality, modularity and collaboration. We believe that bringing rigorous software engineering practices to the energy community has the potential to radically improve productivity and usefulness of software tools. 

Project philosophy: 

- Making code explicit, readable and intuitive counts. “Programs are meant to be read by humans and only incidentally for computers to execute”. 

- Occam’s Razor / Keep It Simple, Stupid (KISS): the best solution is usually also the simplest one. Over-engineering is the root of all evil. 

- A data model is a standard and standards are only useful if they make your life easier. Start with the end outcome in mind. 


## Getting Started

### Install `energydatamodel`

Install the stable release: 
```bash
pip install energydatamodel
```

Install the latest release: 
```bash
pip install git+https://github.com/rebase-energy/EnergyDataModel
```

Install in editable mode for development: 
```bash
git clone
pip install https://github.com/rebase-energy/EnergyDataModel.git
cd EnergyDataModel
pip install -e . 
```

### Quickstart
Create an energy system made up of two sites with co-located solar, wind and batteries and save as a .json. 

```python
import energydatamodel as edm

pvsystem_1 = edm.PVSystem(capacity=2400, surface_azimuth=180, surface_tilt=25)
windturbine_1 = edm.WindTurbine(capacity=3200, hub_height=120, rotor_diameter=100)
battery_1 = edm.Battery(storage_capacity=1000, min_soc=150, max_charge=500. max_discharge=500)

site_1 = edm.Site(assets=[pvsystem_1, windturbine_1, battery_1],
                  latitude=46, 
                  longitude=64)

pvsystem_2 = edm.PVSystem(capacity=2400, surface_azimuth=180, surface_tilt=25)
windturbine_2 = edm.WindTurbine(capacity=3200, hub_height=120, rotor_diameter=100)
battery_2 = edm.Battery(storage_capacity=1000, min_soc=150, max_charge=500. max_discharge=500)

site_2 = edm.Site(assets=[pvsystem_2, windturbine_2, battery_2],
                  latitude=51, 
                  longitude=58)

energysystem = edm.EnergySystem(sites=[site_1, site_2])

energysystem.save_json('my_energysystem.json')
```