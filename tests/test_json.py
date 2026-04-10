"""Tests for JSON round-trip of Entity trees."""

import json

import pytest
from shapely.geometry import Point, Polygon
from timedatamodel import DataType

import energydatamodel as edm
from energydatamodel.geospatial import GeoLocation
from energydatamodel.reference import UnresolvedReferenceError


def _nordic_portfolio():
    t01 = edm.WindTurbine(
        name="T01", capacity=3.5,
        timeseries=[edm.electricity_supply(unit="MW", data_type=DataType.FORECAST)],
    )
    lillgrund = edm.WindFarm(name="Lillgrund", capacity=110, members=[t01])
    site = edm.Site(name="Sweden-Offshore", members=[lillgrund])
    se4 = edm.BiddingZone(name="SE4", timeseries=[edm.spot_price()])
    dk2 = edm.BiddingZone(name="DK2", timeseries=[edm.spot_price()])
    icx = edm.Interconnection(
        name="SE4-DK2",
        from_entity=edm.Reference("SE4"),
        to_entity=edm.Reference("DK2"),
        timeseries=[edm.cross_border_flow()],
    )
    return edm.Portfolio(name="Nordic", members=[site, se4, dk2, icx])


class TestRoundTrip:
    def test_portfolio_round_trip_byte_equal(self):
        p = _nordic_portfolio()
        js = p.to_json()
        restored = edm.Portfolio.from_json(js)
        assert json.dumps(js, default=str) == json.dumps(restored.to_json(), default=str)

    def test_type_tag_on_entities(self):
        p = _nordic_portfolio()
        js = p.to_json()
        assert js["type"] == "Portfolio"
        assert js["members"][0]["type"] == "Site"

    def test_references_resolved_after_from_json(self):
        p = _nordic_portfolio()
        restored = edm.Portfolio.from_json(p.to_json())
        icx = next(m for m in restored.members if isinstance(m, edm.Interconnection))
        assert icx.from_entity.is_resolved()
        assert icx.to_entity.is_resolved()
        assert icx.from_entity.get().name == "SE4"
        assert icx.to_entity.get().name == "DK2"

    def test_unresolved_reference_raises_on_dump(self):
        # Canonical-path serialization fails fast when a string reference can't
        # be resolved against the root — caught at to_json, not at round-trip.
        icx = edm.Interconnection(
            name="X",
            from_entity=edm.Reference("Ghost"),
            to_entity=edm.Reference("Ghost2"),
        )
        wrapper = edm.Portfolio(name="root", members=[icx])
        with pytest.raises(UnresolvedReferenceError):
            wrapper.to_json()

    def test_unresolved_reference_raises_on_load(self):
        # Directly feeding a broken path dict into from_json (e.g. a hand-crafted
        # payload from another system) must still raise at resolve time.
        js = {
            "type": "Portfolio",
            "name": "root",
            "members": [
                {
                    "type": "Interconnection",
                    "name": "X",
                    "from_entity": {"__ref__": "Ghost"},
                    "to_entity": {"__ref__": "Ghost2"},
                }
            ],
        }
        with pytest.raises(UnresolvedReferenceError):
            edm.Portfolio.from_json(js)

    def test_reference_outside_tree_raises_on_dump(self):
        stranger = edm.BiddingZone(name="NO2")
        icx = edm.Interconnection(
            name="X",
            from_entity=edm.Reference(stranger),
            to_entity=edm.Reference(stranger),
        )
        portfolio = edm.Portfolio(name="root", members=[icx])
        with pytest.raises(UnresolvedReferenceError):
            portfolio.to_json()

    def test_id_excluded_by_default(self):
        p = edm.Portfolio(name="x", _id="fixed-id-1")
        js = p.to_json()
        assert "_id" not in js

    def test_id_included_with_flag(self):
        p = edm.Portfolio(name="x", _id="fixed-id-1")
        js = p.to_json(include_ids=True)
        assert js["_id"] == "fixed-id-1"


class TestTimeSeriesDescriptorSerialization:
    def test_descriptor_round_trip(self):
        t = edm.WindTurbine(
            name="T", capacity=3.0,
            timeseries=[edm.electricity_supply(unit="MW", data_type=DataType.FORECAST)],
        )
        wrapper = edm.Portfolio(name="w", members=[t])
        js = wrapper.to_json()
        restored = edm.Portfolio.from_json(js)
        t2 = restored.members[0]
        assert len(t2.timeseries) == 1
        d = t2.timeseries[0]
        assert d.name == "electricity.supply"
        assert d.unit == "MW"
        assert d.data_type == DataType.FORECAST


class TestGeometryRoundTrip:
    """Shapely geometries on the unified ``geometry`` field round-trip."""

    def test_polygon_on_bidding_zone(self):
        poly = Polygon([(0, 0), (2, 0), (2, 1), (0, 1)])
        zone = edm.BiddingZone(name="SE4", geometry=poly)
        wrapper = edm.Portfolio(name="root", members=[zone])
        restored = edm.Portfolio.from_json(wrapper.to_json())
        out = restored.members[0].geometry
        assert isinstance(out, Polygon)
        assert out.equals(poly)

    def test_point_on_wind_turbine(self):
        t = edm.WindTurbine(name="T", capacity=1.0, geometry=Point(13.0, 55.0))
        wrapper = edm.Portfolio(name="root", members=[t])
        restored = edm.Portfolio.from_json(wrapper.to_json())
        out = restored.members[0].geometry
        assert isinstance(out, Point)
        assert out.x == 13.0
        assert out.y == 55.0


class TestValueTypeRoundTrip:
    def test_carrier_round_trip(self):
        carrier = edm.Carrier(name="electricity", type="renewable")
        j = edm.JunctionPoint(name="J", carrier=carrier)
        wrapper = edm.Portfolio(name="root", members=[j])
        restored = edm.Portfolio.from_json(wrapper.to_json())
        out = restored.members[0].carrier
        assert isinstance(out, edm.Carrier)
        assert out.name == "electricity"
        assert out.type == "renewable"


class TestSynchronousArea:
    def test_round_trip_with_nominal_frequency(self):
        nsa = edm.SynchronousArea(
            name="NSA",
            nominal_frequency=50.0,
            timeseries=[edm.grid_frequency()],
        )
        wrapper = edm.Portfolio(name="root", members=[nsa])
        restored = edm.Portfolio.from_json(wrapper.to_json())
        out = restored.members[0]
        assert isinstance(out, edm.SynchronousArea)
        assert out.nominal_frequency == 50.0
        assert len(out.timeseries) == 1
        assert out.timeseries[0].name == "frequency.state.area"
        assert out.timeseries[0].unit == "Hz"
