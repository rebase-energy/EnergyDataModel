"""Tests for Entity, Node, Edge, and the semantic intermediate bases."""

import pytest
from shapely.geometry import Point, Polygon
from timedatamodel import TimeSeriesDescriptor

import energydatamodel as edm


class TestEntity:
    def test_instantiate_direct(self):
        e = edm.Entity(name="root")
        assert e.name == "root"
        assert e._id is None
        assert e.timeseries == []
        assert e.geometry is None

    def test_default_children_empty(self):
        e = edm.Entity(name="x")
        assert e.children() == []

    def test_default_add_child_raises(self):
        e = edm.Entity(name="x")
        with pytest.raises(TypeError, match="does not support"):
            e.add_child(edm.Node(name="y"))

    def test_id_ignored_by_tree_logic(self):
        e = edm.Entity(name="x", _id="abc-123")
        assert e._id == "abc-123"
        assert e.to_properties() == {}

    def test_geometry_point_lat_lon(self):
        e = edm.Entity(name="x", geometry=Point(13.0, 55.0))
        assert e.lon == 13.0
        assert e.lat == 55.0

    def test_geometry_polygon_no_lat_lon(self):
        poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        e = edm.Entity(name="x", geometry=poly)
        assert e.lat is None
        assert e.lon is None
        assert e.centroid is not None


class TestNode:
    def test_members_round_trip(self):
        c = edm.Node(name="c")
        child = edm.Node(name="child")
        c.add_child(child)
        assert c.members == [child]
        assert c.children() == [child]

    def test_add_child_rejects_non_entity(self):
        c = edm.Node(name="c")
        with pytest.raises(TypeError):
            c.add_child("not an entity")


class TestEdge:
    def test_no_members_field(self):
        # Edge sits sibling to Node under Entity; it does not carry
        # members or tz.
        ic = edm.Interconnection(name="x")
        assert not hasattr(ic, "members")
        assert not hasattr(ic, "tz")

    def test_from_to_entity_fields(self):
        ic = edm.Interconnection(
            name="ic",
            from_entity=edm.Reference("A"),
            to_entity=edm.Reference("B"),
            capacity_forward=100,
            capacity_backward=80,
        )
        assert ic.from_entity is not None
        assert ic.to_entity is not None
        assert ic.directed is True


class TestAsset:
    def test_geometry_point(self):
        t = edm.WindTurbine(name="T01", capacity=3.5, geometry=Point(13.0, 55.0))
        assert t.lat == 55.0
        assert t.lon == 13.0


class TestGridNode:
    def test_carrier_field(self):
        c = edm.Carrier(name="electricity", type="renewable")
        j = edm.JunctionPoint(name="J", carrier=c)
        assert j.carrier.name == "electricity"


class TestSensor:
    def test_height_on_subclass(self):
        s = edm.TemperatureSensor(name="T-sensor", height=2.0)
        assert s.height == 2.0


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
    def test_portfolio_is_collection(self):
        p = edm.Portfolio(name="P")
        assert isinstance(p, edm.Collection)
        assert isinstance(p, edm.Node)
        assert isinstance(p, edm.Entity)

    def test_site_is_collection(self):
        s = edm.Site(name="S")
        assert isinstance(s, edm.Collection)

    def test_network_is_collection(self):
        n = edm.Network(name="N")
        assert isinstance(n, edm.Collection)
