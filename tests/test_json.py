"""Tests for JSON round-trip of Element trees."""

import json
from datetime import date, tzinfo
from zoneinfo import ZoneInfo

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


class TestDateAndTzRoundTrip:
    def test_commissioning_date_round_trip(self):
        b = edm.Battery(name="B", commissioning_date=date(2020, 6, 1))
        wrapper = edm.Portfolio(name="root", members=[b])
        restored = edm.Portfolio.from_json(wrapper.to_json())
        out = restored.members[0]
        assert isinstance(out.commissioning_date, date)
        assert out.commissioning_date == date(2020, 6, 1)

    def test_tz_round_trip_zoneinfo(self):
        s = edm.Site(name="S", tz=ZoneInfo("Europe/Stockholm"))
        wrapper = edm.Portfolio(name="root", members=[s])
        restored = edm.Portfolio.from_json(wrapper.to_json())
        out = restored.members[0].tz
        assert isinstance(out, tzinfo)
        assert getattr(out, "key", None) == "Europe/Stockholm"

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


def _kitchen_sink_portfolio():
    """A tree that exercises every round-trip path at once.

    Covers, in one structure:
      * Portfolio → MultiSite → Site → NodeAsset nesting (three levels of
        ``members``).
      * Point and Polygon geometries on assets and areas.
      * ``ZoneInfo`` on two different levels (Collection and House).
      * ``commissioning_date`` on an Asset.
      * Multiple ``TimeSeriesDescriptor``s from the energy vocabulary, mixed
        units/data_types.
      * ``Carrier`` value type on a ``JunctionPoint``.
      * Two ``Interconnection`` edges, one pointing into a deeply nested
        ``BiddingZone`` (path contains multiple segments) and one pointing to
        a sibling — both exercise :class:`Reference` path resolution.
      * ``SynchronousArea`` with ``nominal_frequency``.
    """
    t01 = edm.WindTurbine(
        name="T01", capacity=3.5, hub_height=80,
        geometry=Point(12.78, 55.51),
        commissioning_date=date(2019, 4, 1),
        timeseries=[edm.electricity_supply(unit="MW", data_type=DataType.FORECAST)],
    )
    t02 = edm.WindTurbine(
        name="T02", capacity=3.5, hub_height=80,
        geometry=Point(12.79, 55.52),
        timeseries=[edm.electricity_supply(unit="MW", data_type=DataType.ACTUAL)],
    )
    lillgrund = edm.WindFarm(name="Lillgrund", capacity=110, members=[t01, t02])

    bat = edm.Battery(
        name="Bat1", storage_capacity=10, max_charge=5, max_discharge=5,
        commissioning_date=date(2022, 1, 15),
    )
    hp = edm.HeatPump(
        name="HP1", capacity=8, cop=3.5, energy_source="electricity",
        timeseries=[edm.heating_demand(unit="kW")],
    )
    house = edm.House(
        name="House-42",
        geometry=Point(11.97, 57.71),
        tz=ZoneInfo("Europe/Stockholm"),
        members=[hp, bat],
    )

    site_a = edm.Site(
        name="Sweden-Offshore",
        geometry=Point(12.8, 55.5),
        tz=ZoneInfo("Europe/Stockholm"),
        members=[lillgrund, house],
    )
    multi = edm.MultiSite(name="Nordic-Cluster", members=[site_a])

    se4_poly = Polygon([(12.5, 55.0), (16.5, 55.0), (16.5, 58.0), (12.5, 58.0)])
    dk2_poly = Polygon([(11.0, 54.5), (12.8, 54.5), (12.8, 56.0), (11.0, 56.0)])
    se4 = edm.BiddingZone(
        name="SE4", geometry=se4_poly,
        timeseries=[edm.spot_price(unit="EUR / MWh")],
    )
    dk2 = edm.BiddingZone(
        name="DK2", geometry=dk2_poly,
        timeseries=[edm.spot_price(unit="EUR / MWh")],
    )
    nsa = edm.SynchronousArea(
        name="NSA-Nordic", nominal_frequency=50.0,
        members=[se4, dk2],
        timeseries=[edm.grid_frequency()],
    )

    electricity = edm.Carrier(name="electricity", type="renewable")
    bus = edm.JunctionPoint(name="BusA", carrier=electricity)

    icx_nested = edm.Interconnection(
        name="Line-into-SE4",
        from_entity=edm.Reference("BusA"),
        to_entity=edm.Reference("NSA-Nordic/SE4"),
        capacity_forward=1700, capacity_backward=1300,
        timeseries=[edm.cross_border_flow(unit="MW")],
    )
    icx_sibling = edm.Interconnection(
        name="SE4-DK2",
        from_entity=edm.Reference("NSA-Nordic/SE4"),
        to_entity=edm.Reference("NSA-Nordic/DK2"),
        capacity_forward=2000, capacity_backward=2000,
    )

    return edm.Portfolio(
        name="Kitchen-Sink",
        members=[multi, nsa, bus, icx_nested, icx_sibling],
    )


class TestKitchenSinkRoundTrip:
    """End-to-end round-trip across every feature combined in one tree."""

    def test_byte_equal_round_trip(self):
        p = _kitchen_sink_portfolio()
        js = p.to_json()
        restored = edm.Portfolio.from_json(js)
        assert json.dumps(js, default=str) == json.dumps(restored.to_json(), default=str)

    def test_idempotent_on_second_round_trip(self):
        # dump → load → dump → load must stabilize after the first cycle.
        p = _kitchen_sink_portfolio()
        js1 = p.to_json()
        js2 = edm.Portfolio.from_json(js1).to_json()
        js3 = edm.Portfolio.from_json(js2).to_json()
        assert json.dumps(js2, default=str) == json.dumps(js3, default=str)

    def test_deep_structure_preserved(self):
        restored = edm.Portfolio.from_json(_kitchen_sink_portfolio().to_json())
        multi = restored.members[0]
        assert isinstance(multi, edm.MultiSite)
        site = multi.members[0]
        assert isinstance(site, edm.Site)
        # Site → [WindFarm, House]; WindFarm → [T01, T02]; House → [HP1, Bat1]
        farm, house = site.members
        assert isinstance(farm, edm.WindFarm)
        assert [t.name for t in farm.members] == ["T01", "T02"]
        assert isinstance(house, edm.House)
        assert {type(m).__name__ for m in house.members} == {"HeatPump", "Battery"}

    def test_geometry_types_preserved(self):
        restored = edm.Portfolio.from_json(_kitchen_sink_portfolio().to_json())
        site = restored.members[0].members[0]
        farm = site.members[0]
        assert isinstance(farm.members[0].geometry, Point)
        assert isinstance(site.geometry, Point)
        nsa = restored.members[1]
        for zone in nsa.members:
            assert isinstance(zone.geometry, Polygon)

    def test_tz_at_multiple_levels(self):
        restored = edm.Portfolio.from_json(_kitchen_sink_portfolio().to_json())
        site = restored.members[0].members[0]
        house = site.members[1]
        assert isinstance(site.tz, tzinfo)
        assert isinstance(house.tz, tzinfo)
        assert getattr(site.tz, "key", None) == "Europe/Stockholm"
        assert getattr(house.tz, "key", None) == "Europe/Stockholm"

    def test_references_resolve_across_nesting(self):
        # ``SE4`` and ``DK2`` live under NSA (nested), not as direct siblings
        # of the edges. Reference resolution must search the whole tree.
        restored = edm.Portfolio.from_json(_kitchen_sink_portfolio().to_json())
        edges = [m for m in restored.members if isinstance(m, edm.Interconnection)]
        assert len(edges) == 2
        nested = next(e for e in edges if e.name == "Line-into-SE4")
        sibling = next(e for e in edges if e.name == "SE4-DK2")
        assert nested.from_entity.is_resolved()
        assert nested.to_entity.is_resolved()
        assert nested.to_entity.get().name == "SE4"
        assert isinstance(nested.to_entity.get(), edm.BiddingZone)
        assert sibling.from_entity.get() is not sibling.to_entity.get()
        assert sibling.from_entity.get().name == "SE4"
        assert sibling.to_entity.get().name == "DK2"

    def test_value_types_and_dates_preserved(self):
        restored = edm.Portfolio.from_json(_kitchen_sink_portfolio().to_json())
        bus = next(m for m in restored.members if isinstance(m, edm.JunctionPoint))
        assert isinstance(bus.carrier, edm.Carrier)
        assert bus.carrier.type == "renewable"

        site = restored.members[0].members[0]
        t01 = site.members[0].members[0]
        assert t01.commissioning_date == date(2019, 4, 1)
        battery = site.members[1].members[1]
        assert battery.commissioning_date == date(2022, 1, 15)

    def test_timeseries_descriptors_preserved(self):
        restored = edm.Portfolio.from_json(_kitchen_sink_portfolio().to_json())
        t01 = restored.members[0].members[0].members[0].members[0]
        assert t01.timeseries[0].name == "electricity.supply"
        assert t01.timeseries[0].data_type == DataType.FORECAST
        nsa = restored.members[1]
        assert nsa.nominal_frequency == 50.0
        assert nsa.timeseries[0].unit == "Hz"

    def test_include_ids_flag_round_trips(self):
        # With ``include_ids=True`` every Element's ``_id`` must survive the trip.
        p = _kitchen_sink_portfolio()
        js = p.to_json(include_ids=True)
        restored = edm.Portfolio.from_json(js)
        assert restored._id == p._id
        # Descend to an asset and compare.
        assert restored.members[0].members[0].members[0].members[0]._id == \
               p.members[0].members[0].members[0].members[0]._id
