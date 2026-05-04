"""Tests for JSON round-trip of Element trees — UUID-keyed wire format."""

import json
from datetime import date, tzinfo
from uuid import UUID
from zoneinfo import ZoneInfo

import energydatamodel as edm
import pytest
from energydatamodel.reference import UnresolvedReferenceError
from shapely.geometry import Point, Polygon
from timedatamodel import DataType


def _nordic_portfolio():
    """Tree with two cross-tree edge References — used in many tests below."""
    t01 = edm.wind.WindTurbine(
        name="T01",
        capacity=3.5,
        timeseries=[edm.electricity_supply(unit="MW", data_type=DataType.FORECAST)],
    )
    lillgrund = edm.wind.WindFarm(name="Lillgrund", capacity=110, members=[t01])
    site = edm.Site(name="Sweden-Offshore", members=[lillgrund])
    se4 = edm.BiddingZone(name="SE4", timeseries=[edm.spot_price()])
    dk2 = edm.BiddingZone(name="DK2", timeseries=[edm.spot_price()])
    icx = edm.grid.Interconnection(
        name="SE4-DK2",
        from_element=edm.Reference(se4),
        to_element=edm.Reference(dk2),
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
        assert js["__type__"] == "Portfolio"
        assert js["members"][0]["__type__"] == "Site"

    def test_id_always_emitted(self):
        p = _nordic_portfolio()
        js = p.to_json()
        assert "id" in js
        assert UUID(js["id"]) == p.id

    def test_id_preserved_through_round_trip(self):
        p = _nordic_portfolio()
        restored = edm.Portfolio.from_json(p.to_json())
        assert restored.id == p.id
        # Deep: every nested element keeps its id.
        assert restored.members[0].id == p.members[0].id
        assert restored.members[0].members[0].members[0].id == p.members[0].members[0].members[0].id

    def test_references_use_uuid_wire_format(self):
        p = _nordic_portfolio()
        js = p.to_json()
        icx_js = next(m for m in js["members"] if m["__type__"] == "Interconnection")
        assert "__ref__" in icx_js["from_element"]
        # The ref payload is a UUID string — not a path.
        ref_str = icx_js["from_element"]["__ref__"]
        UUID(ref_str)  # raises if not a UUID

    def test_references_resolve_after_from_json(self):
        p = _nordic_portfolio()
        restored = edm.Portfolio.from_json(p.to_json())
        icx = next(m for m in restored.members if isinstance(m, edm.grid.Interconnection))
        # Refs come back unresolved (single-pass deserialize); resolve on demand.
        assert not icx.from_element.is_resolved()
        icx.from_element.resolve(restored)
        icx.to_element.resolve(restored)
        assert icx.from_element.get().name == "SE4"
        assert icx.to_element.get().name == "DK2"

    def test_unknown_uuid_in_ref_does_not_kill_load(self):
        # Single-pass: a hand-crafted ref to a missing uuid loads fine and
        # only fails at .resolve() time. (Old behavior: died at load.)
        js = {
            "__type__": "Portfolio",
            "name": "root",
            "members": [
                {
                    "__type__": "Interconnection",
                    "name": "X",
                    "from_element": {"__ref__": "01970000-0000-7000-8000-000000000000"},
                    "to_element": {"__ref__": "01970000-0000-7000-8000-000000000001"},
                }
            ],
        }
        portfolio = edm.Portfolio.from_json(js)
        icx = portfolio.members[0]
        with pytest.raises(UnresolvedReferenceError):
            icx.from_element.resolve(portfolio)


class TestTimeSeriesDescriptorSerialization:
    def test_descriptor_round_trip(self):
        t = edm.wind.WindTurbine(
            name="T",
            capacity=3.0,
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
        t = edm.wind.WindTurbine(name="T", capacity=1.0, geometry=Point(13.0, 55.0))
        wrapper = edm.Portfolio(name="root", members=[t])
        restored = edm.Portfolio.from_json(wrapper.to_json())
        out = restored.members[0].geometry
        assert isinstance(out, Point)
        assert out.x == 13.0
        assert out.y == 55.0


class TestValueTypeRoundTrip:
    def test_carrier_round_trip(self):
        carrier = edm.grid.Carrier(name="electricity", type="renewable")
        j = edm.grid.JunctionPoint(name="J", carrier=carrier)
        wrapper = edm.Portfolio(name="root", members=[j])
        restored = edm.Portfolio.from_json(wrapper.to_json())
        out = restored.members[0].carrier
        assert isinstance(out, edm.grid.Carrier)
        assert out.name == "electricity"
        assert out.type == "renewable"


class TestDateAndTzRoundTrip:
    def test_commissioning_date_round_trip(self):
        b = edm.battery.Battery(name="B", commissioning_date=date(2020, 6, 1))
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


class TestExtraValidation:
    """`extra` is restricted to JSON-native scalars; rich types raise."""

    def test_scalar_dict_round_trip(self):
        site = edm.Site(
            name="x",
            extra={
                "owner": "Acme",
                "tags": ["a", "b"],
                "nested": {"x": 1, "y": [1, 2, 3]},
                "asset_id_legacy": 17,
            },
        )
        restored = edm.Element.from_json(site.to_json())
        assert restored.extra == site.extra

    def test_element_in_extra_raises(self):
        zone = edm.BiddingZone(name="Z")
        site = edm.Site(name="x", extra={"linked": zone})
        with pytest.raises(TypeError, match="non-JSON-scalar"):
            site.to_json()

    def test_enum_in_extra_raises(self):
        site = edm.Site(name="x", extra={"q": edm.Quantity.ELECTRICITY})
        with pytest.raises(TypeError, match="Enum"):
            site.to_json()


def _kitchen_sink_portfolio():
    """A tree exercising every round-trip path at once.

    Uses :class:`Reference` constructed from Element instances (the canonical
    UUID-bearing form) rather than path strings.
    """
    t01 = edm.wind.WindTurbine(
        name="T01",
        capacity=3.5,
        hub_height=80,
        geometry=Point(12.78, 55.51),
        commissioning_date=date(2019, 4, 1),
        timeseries=[edm.electricity_supply(unit="MW", data_type=DataType.FORECAST)],
    )
    t02 = edm.wind.WindTurbine(
        name="T02",
        capacity=3.5,
        hub_height=80,
        geometry=Point(12.79, 55.52),
        timeseries=[edm.electricity_supply(unit="MW", data_type=DataType.ACTUAL)],
    )
    lillgrund = edm.wind.WindFarm(name="Lillgrund", capacity=110, members=[t01, t02])

    bat = edm.battery.Battery(
        name="Bat1",
        storage_capacity=10,
        max_charge=5,
        max_discharge=5,
        commissioning_date=date(2022, 1, 15),
    )
    hp = edm.heatpump.HeatPump(
        name="HP1",
        capacity=8,
        cop=3.5,
        energy_source="electricity",
        timeseries=[edm.heating_demand(unit="kW")],
    )
    house = edm.building.House(
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
        name="SE4",
        geometry=se4_poly,
        timeseries=[edm.spot_price(unit="EUR / MWh")],
    )
    dk2 = edm.BiddingZone(
        name="DK2",
        geometry=dk2_poly,
        timeseries=[edm.spot_price(unit="EUR / MWh")],
    )
    nsa = edm.SynchronousArea(
        name="NSA-Nordic",
        nominal_frequency=50.0,
        members=[se4, dk2],
        timeseries=[edm.grid_frequency()],
    )

    electricity = edm.grid.Carrier(name="electricity", type="renewable")
    bus = edm.grid.JunctionPoint(name="BusA", carrier=electricity)

    icx_nested = edm.grid.Interconnection(
        name="Line-into-SE4",
        from_element=edm.Reference(bus),
        to_element=edm.Reference(se4),
        capacity_forward=1700,
        capacity_backward=1300,
        timeseries=[edm.cross_border_flow(unit="MW")],
    )
    icx_sibling = edm.grid.Interconnection(
        name="SE4-DK2",
        from_element=edm.Reference(se4),
        to_element=edm.Reference(dk2),
        capacity_forward=2000,
        capacity_backward=2000,
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
        farm, house = site.members
        assert isinstance(farm, edm.wind.WindFarm)
        assert [t.name for t in farm.members] == ["T01", "T02"]
        assert isinstance(house, edm.building.House)
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
        # SE4/DK2 live under NSA (nested), not as direct siblings of the edges.
        # Reference resolution must search the whole tree.
        restored = edm.Portfolio.from_json(_kitchen_sink_portfolio().to_json())
        edges = [m for m in restored.members if isinstance(m, edm.grid.Interconnection)]
        assert len(edges) == 2
        index = restored.index()
        nested = next(e for e in edges if e.name == "Line-into-SE4")
        sibling = next(e for e in edges if e.name == "SE4-DK2")
        nested.from_element.resolve(index)
        nested.to_element.resolve(index)
        sibling.from_element.resolve(index)
        sibling.to_element.resolve(index)
        assert nested.to_element.get().name == "SE4"
        assert isinstance(nested.to_element.get(), edm.BiddingZone)
        assert sibling.from_element.get() is not sibling.to_element.get()
        assert sibling.from_element.get().name == "SE4"
        assert sibling.to_element.get().name == "DK2"

    def test_value_types_and_dates_preserved(self):
        restored = edm.Portfolio.from_json(_kitchen_sink_portfolio().to_json())
        bus = next(m for m in restored.members if isinstance(m, edm.grid.JunctionPoint))
        assert isinstance(bus.carrier, edm.grid.Carrier)
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


class TestExcludeFields:
    """Tests for the ``exclude_fields`` parameter on ``element_to_json`` / ``to_json``."""

    def test_exclude_members_produces_flat_dict(self):
        p = edm.Portfolio(
            name="P",
            members=[
                edm.Site(name="S", members=[edm.wind.WindTurbine(name="T", capacity=3.0)]),
            ],
        )
        js = p.to_json(exclude_fields={"members"})
        assert js["__type__"] == "Portfolio"
        assert js["name"] == "P"
        assert "members" not in js

    def test_exclude_applies_recursively(self):
        portfolio = edm.Portfolio(
            name="P",
            members=[
                edm.Site(name="S", members=[edm.wind.WindTurbine(name="T", capacity=3.0)]),
            ],
        )
        js = portfolio.to_json(exclude_fields={"capacity"})
        turbine = js["members"][0]["members"][0]
        assert turbine["__type__"] == "WindTurbine"
        assert "capacity" not in turbine

    def test_exclude_from_to_element_on_edge(self):
        a = edm.BiddingZone(name="A")
        b = edm.BiddingZone(name="B")
        ic = edm.grid.Interconnection(
            name="IC",
            from_element=edm.Reference(a),
            to_element=edm.Reference(b),
            capacity_forward=1000,
        )
        js = edm.element_to_json(ic, exclude_fields={"from_element", "to_element"})
        assert js["__type__"] == "Interconnection"
        assert js["name"] == "IC"
        assert js["capacity_forward"] == 1000
        assert "from_element" not in js
        assert "to_element" not in js

    def test_exclude_fields_default_unchanged(self):
        p = _nordic_portfolio()
        assert p.to_json() == edm.element_to_json(p, exclude_fields=None)


class TestElementToStorageDict:
    """Tests for ``element_to_storage_dict`` — the flat-row wrapper."""

    def test_excludes_children(self):
        p = edm.Portfolio(
            name="Europe",
            members=[
                edm.Site(name="Offshore", members=[edm.wind.WindTurbine(name="T", capacity=3.0)]),
            ],
        )
        d = edm.element_to_storage_dict(p)
        assert d["__type__"] == "Portfolio"
        assert d["name"] == "Europe"
        assert "members" not in d

    def test_preserves_own_fields(self):
        t = edm.wind.WindTurbine(
            name="T01",
            capacity=3.5,
            hub_height=80,
            geometry=Point(3.0, 55.0),
        )
        d = edm.element_to_storage_dict(t)
        assert d["__type__"] == "WindTurbine"
        assert d["name"] == "T01"
        assert d["capacity"] == 3.5
        assert d["hub_height"] == 80
        assert d["geometry"]["__geometry__"] is True

    def test_extra_excludes_for_edges(self):
        a = edm.BiddingZone(name="A")
        b = edm.BiddingZone(name="B")
        line = edm.grid.Line(
            name="L1",
            capacity=500,
            from_element=edm.Reference(a),
            to_element=edm.Reference(b),
        )
        d = edm.element_to_storage_dict(line, extra_excludes={"from_element", "to_element"})
        assert d["__type__"] == "Line"
        assert d["capacity"] == 500
        assert "from_element" not in d
        assert "to_element" not in d

    def test_round_trip_single_element(self):
        t = edm.wind.WindTurbine(
            name="T01",
            capacity=3.5,
            hub_height=80,
            commissioning_date=date(2020, 1, 1),
            geometry=Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        )
        d = edm.element_to_storage_dict(t)
        restored = edm.element_from_json(d)
        assert isinstance(restored, edm.wind.WindTurbine)
        assert restored.name == "T01"
        assert restored.id == t.id
        assert restored.capacity == 3.5
        assert restored.hub_height == 80
        assert restored.commissioning_date == date(2020, 1, 1)
        assert restored.geometry.equals(t.geometry)

    def test_round_trip_preserves_tz(self):
        s = edm.Site(name="S", tz=ZoneInfo("Europe/Stockholm"))
        d = edm.element_to_storage_dict(s)
        restored = edm.element_from_json(d)
        assert isinstance(restored.tz, ZoneInfo)
        assert str(restored.tz) == "Europe/Stockholm"

    def test_round_trip_preserves_sensor_height(self):
        ts = edm.weather.TemperatureSensor(name="Temp", height=10.0)
        d = edm.element_to_storage_dict(ts)
        restored = edm.element_from_json(d)
        assert isinstance(restored, edm.weather.TemperatureSensor)
