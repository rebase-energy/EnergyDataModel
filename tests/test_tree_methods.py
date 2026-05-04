"""Tests for children(), add_child(), and to_properties() methods on EDM classes."""

import energydatamodel as edm
import pytest
from shapely.geometry import Point
from timedatamodel import DataType, TimeSeriesDescriptor

# ---------------------------------------------------------------------------
# children()
# ---------------------------------------------------------------------------


class TestChildren:
    def test_portfolio_children_members(self):
        t01 = edm.wind.WindTurbine(name="T01", capacity=3.5)
        site = edm.Site(name="Sweden")
        portfolio = edm.Portfolio(name="Europe", members=[site, t01])
        children = portfolio.children()
        assert len(children) == 2
        names = {c.name for c in children}
        assert names == {"Sweden", "T01"}

    def test_site_children(self):
        t01 = edm.wind.WindTurbine(name="T01", capacity=3.5)
        t02 = edm.wind.WindTurbine(name="T02", capacity=3.5)
        site = edm.Site(name="Sweden", members=[t01, t02])
        children = site.children()
        assert len(children) == 2
        assert children[0].name == "T01"
        assert children[1].name == "T02"

    def test_windfarm_children(self):
        t01 = edm.wind.WindTurbine(name="T01", capacity=3.5)
        t02 = edm.wind.WindTurbine(name="T02", capacity=3.5)
        farm = edm.wind.WindFarm(name="Lillgrund", capacity=110, members=[t01, t02])
        children = farm.children()
        assert len(children) == 2
        assert all(isinstance(c, edm.wind.WindTurbine) for c in children)

    def test_windfarm_no_children(self):
        farm = edm.wind.WindFarm(name="Empty", capacity=0)
        assert farm.children() == []

    def test_pvsystem_children(self):
        arr = edm.solar.PVArray(capacity=5.0, surface_tilt=25, surface_azimuth=180)
        pv = edm.solar.PVSystem(name="PV01", members=[arr])
        children = pv.children()
        assert len(children) == 1
        assert isinstance(children[0], edm.solar.PVArray)

    def test_pvsystem_does_not_auto_create_array(self):
        # The old back-compat behavior of auto-creating a PVArray from
        # top-level capacity/tilt/azimuth is gone — empty PVSystem stays empty.
        pv = edm.solar.PVSystem(name="PV", capacity=5, surface_azimuth=180, surface_tilt=25)
        assert pv.members == []

    def test_windturbine_no_children(self):
        t = edm.wind.WindTurbine(name="T01", capacity=3.5)
        assert t.children() == []

    def test_battery_no_children(self):
        b = edm.battery.Battery(name="B01", storage_capacity=100)
        assert b.children() == []

    def test_building_children(self):
        hp = edm.heatpump.HeatPump(name="HP01", capacity=10, cop=3.0, energy_source="air")
        building = edm.building.Building(name="B1", members=[hp])
        children = building.children()
        assert len(children) == 1
        assert children[0].name == "HP01"

    def test_house_children(self):
        pv = edm.solar.PVSystem(name="Roof-PV", capacity=5)
        house = edm.building.House(name="H1", members=[pv])
        children = house.children()
        assert len(children) == 1
        assert children[0].name == "Roof-PV"

    def test_empty_portfolio(self):
        p = edm.Portfolio(name="Empty")
        assert p.children() == []

    def test_empty_site(self):
        s = edm.Site(name="Empty")
        assert s.children() == []


class TestChildrenRecursiveWalk:
    """Test that children() enables generic tree walking."""

    def test_full_tree_walk(self):
        t01 = edm.wind.WindTurbine(name="T01", capacity=3.5)
        t02 = edm.wind.WindTurbine(name="T02", capacity=3.5)
        farm = edm.wind.WindFarm(name="Lillgrund", capacity=110, members=[t01, t02])
        site = edm.Site(name="Sweden", members=[farm])
        portfolio = edm.Portfolio(name="Europe", members=[site])

        names = []

        def walk(obj):
            names.append(obj.name)
            for child in obj.children():
                walk(child)

        walk(portfolio)
        assert names == ["Europe", "Sweden", "Lillgrund", "T01", "T02"]


# ---------------------------------------------------------------------------
# add_child()
# ---------------------------------------------------------------------------


class TestAddChild:
    def test_portfolio_add_site(self):
        p = edm.Portfolio(name="Europe")
        s = edm.Site(name="Sweden")
        p.add_child(s)
        assert len(p.members) == 1
        assert p.members[0].name == "Sweden"

    def test_portfolio_add_asset(self):
        p = edm.Portfolio(name="Europe")
        t = edm.wind.WindTurbine(name="T01", capacity=3.5)
        p.add_child(t)
        assert len(p.members) == 1
        assert p.members[0].name == "T01"

    def test_portfolio_add_sub_portfolio(self):
        parent = edm.Portfolio(name="Europe")
        child = edm.Portfolio(name="Nordics")
        parent.add_child(child)
        assert len(parent.members) == 1
        assert parent.members[0].name == "Nordics"

    def test_site_add_asset(self):
        s = edm.Site(name="Sweden")
        t = edm.wind.WindTurbine(name="T01", capacity=3.5)
        s.add_child(t)
        assert len(s.members) == 1

    def test_windfarm_add_turbine(self):
        farm = edm.wind.WindFarm(name="Lillgrund", capacity=110)
        t = edm.wind.WindTurbine(name="T01", capacity=3.5)
        farm.add_child(t)
        assert len(farm.members) == 1

    def test_windfarm_accepts_any_element(self):
        # Real wind farms contain met masts, transformers, substations, ...
        # so add_child accepts any Element, not just WindTurbine.
        farm = edm.wind.WindFarm(name="Lillgrund", capacity=110)
        bus = edm.grid.JunctionPoint(name="Bus1")
        farm.add_child(bus)
        assert len(farm.members) == 1

    def test_pvsystem_add_array(self):
        pv = edm.solar.PVSystem(name="PV01")
        arr = edm.solar.PVArray(capacity=5.0, surface_tilt=25, surface_azimuth=180)
        pv.add_child(arr)
        assert len(pv.members) == 1

    def test_pvsystem_accepts_any_element(self):
        # PVSystem no longer enforces PVArray-only children.
        pv = edm.solar.PVSystem(name="PV01")
        sensor = edm.weather.RadiationSensor(name="R1", height=2.0)
        pv.add_child(sensor)
        assert len(pv.members) == 1

    def test_building_add_asset(self):
        b = edm.building.Building(name="B1")
        hp = edm.heatpump.HeatPump(name="HP01", capacity=10, cop=3.0, energy_source="air")
        b.add_child(hp)
        assert len(b.members) == 1

    def test_windturbine_accepts_any_element(self):
        # In the new flat ontology, every Node supports add_child by default.
        # WindTurbine doesn't override it, so it accepts any Element member.
        t = edm.wind.WindTurbine(name="T01", capacity=3.5)
        t2 = edm.wind.WindTurbine(name="T02", capacity=3.5)
        t.add_child(t2)
        assert len(t.members) == 1


class TestAddChildRoundTrip:
    """Test that add_child() + children() round-trips correctly (for DB reconstruction)."""

    def test_build_tree_with_add_child(self):
        portfolio = edm.Portfolio(name="Europe")
        site = edm.Site(name="Sweden")
        farm = edm.wind.WindFarm(name="Lillgrund", capacity=110)
        t01 = edm.wind.WindTurbine(name="T01", capacity=3.5)
        t02 = edm.wind.WindTurbine(name="T02", capacity=3.5)

        farm.add_child(t01)
        farm.add_child(t02)
        site.add_child(farm)
        portfolio.add_child(site)

        assert len(portfolio.children()) == 1
        assert portfolio.children()[0].name == "Sweden"
        assert len(portfolio.children()[0].children()) == 1
        assert portfolio.children()[0].children()[0].name == "Lillgrund"
        turbines = portfolio.children()[0].children()[0].children()
        assert len(turbines) == 2
        assert {t.name for t in turbines} == {"T01", "T02"}


# ---------------------------------------------------------------------------
# to_properties()
# ---------------------------------------------------------------------------


class TestToProperties:
    def test_windturbine(self):
        t = edm.wind.WindTurbine(
            name="T01",
            capacity=3.5,
            hub_height=80,
            geometry=Point(3.0, 55.0),
        )
        props = t.to_properties()
        assert props == {"capacity": 3.5, "hub_height": 80}
        assert "name" not in props
        assert "geometry" not in props

    def test_windfarm_excludes_members(self):
        t01 = edm.wind.WindTurbine(name="T01", capacity=3.5)
        farm = edm.wind.WindFarm(name="Lillgrund", capacity=110, members=[t01])
        props = farm.to_properties()
        assert props == {"capacity": 110}
        assert "members" not in props

    def test_pvsystem_excludes_members(self):
        arr = edm.solar.PVArray(capacity=5.0, surface_tilt=25, surface_azimuth=180)
        pv = edm.solar.PVSystem(name="PV01", capacity=10, surface_tilt=25, surface_azimuth=180, members=[arr])
        props = pv.to_properties()
        assert "members" not in props
        assert "capacity" in props

    def test_battery(self):
        b = edm.battery.Battery(name="B01", storage_capacity=100, min_soc=0.1)
        props = b.to_properties()
        assert props["storage_capacity"] == 100
        assert props["min_soc"] == 0.1
        assert "name" not in props

    def test_site_empty_properties(self):
        s = edm.Site(name="Sweden", geometry=Point(13.0, 55.0))
        props = s.to_properties()
        assert props == {}

    def test_portfolio_empty_properties(self):
        p = edm.Portfolio(name="Europe")
        props = p.to_properties()
        assert props == {}

    def test_none_values_excluded(self):
        t = edm.wind.WindTurbine(name="T01", capacity=3.5)
        props = t.to_properties()
        assert "hub_height" not in props
        assert "rotor_diameter" not in props

    def test_timeseries_excluded(self):
        desc = TimeSeriesDescriptor(name="electricity.supply", data_type=DataType.FORECAST)
        t = edm.wind.WindTurbine(name="T01", capacity=3.5, timeseries=[desc])
        props = t.to_properties()
        assert "timeseries" not in props

    def test_building_excludes_members(self):
        hp = edm.heatpump.HeatPump(name="HP01", capacity=10, cop=3.0, energy_source="air")
        b = edm.building.Building(name="B1", type="commercial", members=[hp])
        props = b.to_properties()
        assert "members" not in props
        assert props.get("type") == "commercial"

    def test_synchronous_area_nominal_frequency(self):
        nsa = edm.SynchronousArea(name="NSA", nominal_frequency=50.0)
        props = nsa.to_properties()
        assert props == {"nominal_frequency": 50.0}
