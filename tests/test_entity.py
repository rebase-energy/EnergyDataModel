"""Tests for Element, Node, Edge, Asset mixin, and the role intermediates."""

from uuid import UUID

import energydatamodel as edm
import pytest
from shapely.geometry import Point, Polygon


class TestElement:
    def test_instantiate_direct(self):
        e = edm.Element(name="root")
        assert e.name == "root"
        assert isinstance(e.id, UUID)
        assert e.timeseries == []
        assert e.geometry is None

    def test_id_unique_per_instance(self):
        a = edm.Element(name="a")
        b = edm.Element(name="b")
        assert a.id != b.id

    def test_id_preserved_when_passed(self):
        custom = UUID("01970000-0000-7000-8000-000000000000")
        e = edm.Element(name="x", id=custom)
        assert e.id == custom

    def test_default_children_empty(self):
        e = edm.Element(name="x")
        assert e.children() == []

    def test_default_add_child_raises(self):
        e = edm.Element(name="x")
        with pytest.raises(TypeError, match="does not support"):
            e.add_child(edm.Node(name="y"))

    def test_id_excluded_from_to_properties(self):
        e = edm.Element(name="x")
        assert e.to_properties() == {}

    def test_geometry_point_lat_lon(self):
        e = edm.Element(name="x", geometry=Point(13.0, 55.0))
        assert e.longitude == 13.0
        assert e.latitude == 55.0

    def test_geometry_polygon_no_lat_lon(self):
        poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        e = edm.Element(name="x", geometry=poly)
        assert e.latitude is None
        assert e.longitude is None
        assert e.centroid is not None

    def test_lat_lon_kwargs_build_point(self):
        e = edm.Element(name="x", lat=55.0, lon=13.0)
        assert isinstance(e.geometry, Point)
        assert e.geometry.x == 13.0
        assert e.geometry.y == 55.0
        assert e.latitude == 55.0
        assert e.longitude == 13.0

    def test_geometry_tuple_shorthand(self):
        e = edm.Element(name="x", geometry=(13.0, 55.0))
        assert isinstance(e.geometry, Point)
        assert (e.geometry.x, e.geometry.y) == (13.0, 55.0)

    def test_lat_lon_with_geometry_raises(self):
        with pytest.raises(ValueError, match="either"):
            edm.Element(name="x", lat=55.0, lon=13.0, geometry=Point(1.0, 2.0))

    def test_lat_alone_raises(self):
        with pytest.raises(ValueError, match="together"):
            edm.Element(name="x", lat=55.0)

    def test_out_of_bounds_raises(self):
        with pytest.raises(ValueError, match="WGS84"):
            edm.Element(name="x", lat=200.0, lon=10.0)

    def test_subclass_lat_lon(self):
        t = edm.wind.WindTurbine(name="t", lat=59.9, lon=10.5, capacity=3.0)
        assert (t.geometry.x, t.geometry.y) == (10.5, 59.9)


class TestNode:
    def test_members_round_trip(self):
        c = edm.Node(name="c")
        child = edm.Node(name="child")
        c.add_child(child)
        assert c.members == [child]
        assert c.children() == [child]

    def test_add_child_rejects_non_element(self):
        c = edm.Node(name="c")
        with pytest.raises(TypeError):
            c.add_child("not an element")


class TestEdge:
    def test_no_members_field(self):
        # Edge sits sibling to Node under Element; does not carry members or tz.
        ic = edm.grid.Interconnection(name="x")
        assert not hasattr(ic, "members")
        assert not hasattr(ic, "tz")

    def test_from_to_element_fields(self):
        a = edm.BiddingZone(name="A")
        b = edm.BiddingZone(name="B")
        ic = edm.grid.Interconnection(
            name="ic",
            from_element=edm.Reference(a),
            to_element=edm.Reference(b),
            capacity_forward=100,
            capacity_backward=80,
        )
        assert ic.from_element.id == a.id
        assert ic.to_element.id == b.id
        assert ic.directed is True


class TestAssetMixin:
    """Asset is a mixin — marker for physical equipment on both graph sides."""

    def test_node_asset_classes_are_asset(self):
        assert isinstance(edm.wind.WindTurbine(name="t"), edm.Asset)
        assert isinstance(edm.battery.Battery(name="b"), edm.Asset)
        assert isinstance(edm.heatpump.HeatPump(name="h"), edm.Asset)
        assert isinstance(edm.building.Building(name="b"), edm.Asset)

    def test_sensor_and_gridnode_are_asset(self):
        assert isinstance(edm.weather.TemperatureSensor(name="t"), edm.Asset)
        assert isinstance(edm.grid.Meter(name="m"), edm.Asset)
        assert isinstance(edm.grid.DeliveryPoint(name="d"), edm.Asset)
        assert isinstance(edm.grid.JunctionPoint(name="j"), edm.Asset)
        assert isinstance(edm.grid.Transformer(name="t"), edm.Asset)

    def test_edge_equipment_is_asset(self):
        assert isinstance(edm.grid.Line(name="l"), edm.Asset)
        assert isinstance(edm.grid.Pipe(name="p"), edm.Asset)
        assert isinstance(edm.grid.Interconnection(name="ic"), edm.Asset)

    def test_area_is_not_asset(self):
        assert not isinstance(edm.BiddingZone(name="z"), edm.Asset)
        assert not isinstance(edm.Country(name="c"), edm.Asset)

    def test_collection_is_not_asset(self):
        assert not isinstance(edm.Portfolio(name="p"), edm.Asset)
        assert not isinstance(edm.Site(name="s"), edm.Asset)
        assert not isinstance(edm.Region(name="r"), edm.Asset)

    def test_commissioning_date(self):
        from datetime import date

        t = edm.wind.WindTurbine(name="t", commissioning_date=date(2020, 1, 1))
        assert t.commissioning_date == date(2020, 1, 1)


class TestNodeAssetEdgeAsset:
    def test_wind_turbine_is_node_asset(self):
        t = edm.wind.WindTurbine(name="t", capacity=3.0)
        assert isinstance(t, edm.NodeAsset)
        assert isinstance(t, edm.Node)
        assert isinstance(t, edm.Asset)
        assert isinstance(t, edm.Element)

    def test_line_is_edge_asset(self):
        line = edm.grid.Line(name="L", capacity=100)
        assert isinstance(line, edm.grid.EdgeAsset)
        assert isinstance(line, edm.Edge)
        assert isinstance(line, edm.Asset)
        assert isinstance(line, edm.Element)
        assert not isinstance(line, edm.Node)

    def test_sensor_mro(self):
        s = edm.weather.TemperatureSensor(name="t", height=2.0)
        mro_names = [c.__name__ for c in type(s).__mro__]
        assert "Sensor" in mro_names
        assert "NodeAsset" in mro_names
        assert "Node" in mro_names
        assert "Asset" in mro_names
        assert "Element" in mro_names


class TestGridNode:
    def test_carrier_field(self):
        c = edm.grid.Carrier(name="electricity", type="renewable")
        j = edm.grid.JunctionPoint(name="J", carrier=c)
        assert j.carrier.name == "electricity"


class TestSensor:
    def test_height_on_base(self):
        s = edm.weather.TemperatureSensor(name="T-sensor", height=2.0)
        assert s.height == 2.0

    def test_all_weather_sensors_inherit_height(self):
        for cls in (
            edm.weather.TemperatureSensor,
            edm.weather.WindSpeedSensor,
            edm.weather.RadiationSensor,
            edm.weather.RainSensor,
            edm.weather.HumiditySensor,
        ):
            s = cls(name="s", height=1.5)
            assert s.height == 1.5


class TestArea:
    def test_bidding_zone(self):
        z = edm.BiddingZone(name="SE-SE1")
        assert isinstance(z, edm.Area)
        assert isinstance(z, edm.Node)

    def test_synchronous_area_default_frequency(self):
        nsa = edm.SynchronousArea(name="NSA")
        assert nsa.nominal_frequency == 50.0
        assert isinstance(nsa, edm.Area)

    def test_synchronous_area_60hz(self):
        wecc = edm.SynchronousArea(name="WECC", nominal_frequency=60.0)
        assert wecc.nominal_frequency == 60.0


class TestCollection:
    def test_portfolio_is_collection_not_asset(self):
        p = edm.Portfolio(name="P")
        assert isinstance(p, edm.Collection)
        assert isinstance(p, edm.Element)
        assert not isinstance(p, edm.Asset)

    def test_site_is_collection(self):
        s = edm.Site(name="S")
        assert isinstance(s, edm.Collection)

    def test_network_is_collection(self):
        n = edm.grid.Network(name="N")
        assert isinstance(n, edm.Collection)


class TestDiamondMRO:
    def test_wind_turbine_construction(self):
        """Constructing a diamond class should initialize Element fields once."""
        from datetime import date

        t = edm.wind.WindTurbine(
            name="t",
            commissioning_date=date(2020, 1, 1),
            capacity=3.0,
            hub_height=100.0,
        )
        assert t.name == "t"
        assert t.commissioning_date == date(2020, 1, 1)
        assert t.capacity == 3.0
        assert t.hub_height == 100.0
        # Inherited collection field initialized exactly once to an empty list.
        assert t.members == []
        assert t.timeseries == []

    def test_line_construction(self):
        a = edm.grid.JunctionPoint(name="A")
        b = edm.grid.JunctionPoint(name="B")
        line = edm.grid.Line(
            name="L",
            from_element=edm.Reference(a),
            to_element=edm.Reference(b),
            capacity=100.0,
        )
        assert line.name == "L"
        assert line.capacity == 100.0
        assert line.directed is True
        assert line.from_element.id == a.id
