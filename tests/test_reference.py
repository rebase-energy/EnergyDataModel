"""Tests for Reference[T] — UUID-based cross-tree references and Index."""

from uuid import UUID, uuid4

import energydatamodel as edm
import pytest
from energydatamodel.reference import UnresolvedReferenceError


def _make_tree():
    se4 = edm.BiddingZone(name="SE4")
    dk2 = edm.BiddingZone(name="DK2")
    icx = edm.grid.Interconnection(
        name="SE4-DK2",
        from_element=edm.Reference(se4),
        to_element=edm.Reference(dk2),
    )
    return edm.Portfolio(name="Nordic", members=[se4, dk2, icx]), se4, dk2, icx


class TestReferenceConstruction:
    def test_from_element_captures_id(self):
        zone = edm.BiddingZone(name="SE4")
        ref = edm.Reference(zone)
        assert ref.id == zone.id
        assert ref.is_resolved()

    def test_from_uuid(self):
        u = uuid4()
        ref = edm.Reference(u)
        assert ref.id == u
        assert not ref.is_resolved()

    def test_from_uuid_str(self):
        s = "01970000-0000-7000-8000-000000000000"
        ref = edm.Reference(s)
        assert ref.id == UUID(s)
        assert not ref.is_resolved()

    def test_invalid_target_type_raises(self):
        with pytest.raises(TypeError):
            edm.Reference(42)


class TestResolve:
    def test_resolve_against_tree(self):
        portfolio, se4, _, icx = _make_tree()
        # The Reference was constructed from an Element, so it's already
        # resolved. Build a UUID-only Reference to exercise resolution.
        ref = edm.Reference(se4.id)
        assert not ref.is_resolved()
        ref.resolve(portfolio)
        assert ref.is_resolved()
        assert ref.get() is se4

    def test_resolve_against_index(self):
        portfolio, se4, _, _ = _make_tree()
        index = portfolio.index()
        ref = edm.Reference(se4.id)
        assert ref.resolve(index) is se4

    def test_resolve_unknown_uuid_raises(self):
        portfolio, *_ = _make_tree()
        ref = edm.Reference(uuid4())
        with pytest.raises(UnresolvedReferenceError):
            ref.resolve(portfolio)

    def test_resolve_is_idempotent(self):
        portfolio, se4, _, _ = _make_tree()
        ref = edm.Reference(se4.id)
        first = ref.resolve(portfolio)
        second = ref.resolve(portfolio)
        assert first is second is se4

    def test_get_unresolved_raises(self):
        ref = edm.Reference(uuid4())
        with pytest.raises(UnresolvedReferenceError):
            ref.get()


class TestPathHelper:
    """``Reference.path`` — debug helper, not part of the wire format."""

    def test_path_of_resolved(self):
        portfolio, _, _, _ = _make_tree()
        t01 = edm.wind.WindTurbine(name="T01")
        farm = edm.wind.WindFarm(name="Lillgrund", members=[t01])
        site = edm.Site(name="Sweden", members=[farm])
        portfolio = edm.Portfolio(name="Nordic", members=[site])
        ref = edm.Reference(t01)
        assert ref.path(portfolio) == ("Nordic", "Sweden", "Lillgrund", "T01")

    def test_path_outside_tree_raises(self):
        portfolio, *_ = _make_tree()
        stranger = edm.BiddingZone(name="NO2")
        ref = edm.Reference(stranger)
        with pytest.raises(UnresolvedReferenceError):
            ref.path(portfolio)

    def test_name_with_slash_preserved_in_path_tuple(self):
        weird = edm.BiddingZone(name="A/B")
        portfolio = edm.Portfolio(name="P", members=[weird])
        ref = edm.Reference(weird)
        assert ref.path(portfolio) == ("P", "A/B")


class TestIndex:
    def test_build_index_on_tree(self):
        portfolio, se4, dk2, icx = _make_tree()
        index = portfolio.index()
        assert portfolio.id in index
        assert se4.id in index
        assert dk2.id in index
        assert icx.id in index
        assert index[se4.id] is se4

    def test_index_size(self):
        portfolio, *_ = _make_tree()
        index = portfolio.index()
        assert len(index) == 4  # Portfolio + SE4 + DK2 + Interconnection

    def test_index_missing_raises(self):
        portfolio, *_ = _make_tree()
        index = portfolio.index()
        with pytest.raises(UnresolvedReferenceError):
            index[uuid4()]

    def test_duplicate_uuid_raises(self):
        a = edm.BiddingZone(name="A")
        b = edm.BiddingZone(name="B", id=a.id)
        portfolio = edm.Portfolio(name="P", members=[a, b])
        with pytest.raises(ValueError, match="Duplicate UUID"):
            portfolio.index()


class TestEquality:
    def test_eq_by_id(self):
        zone = edm.BiddingZone(name="SE4")
        a = edm.Reference(zone)
        b = edm.Reference(zone.id)  # different object, same id
        assert a == b
        assert hash(a) == hash(b)

    def test_neq_different_id(self):
        a = edm.Reference(uuid4())
        b = edm.Reference(uuid4())
        assert a != b


class TestEdgeAutoWrap:
    def test_bare_element_endpoint_auto_wrapped(self):
        """Edge.__post_init__ wraps bare Element endpoints in Reference."""
        a = edm.BiddingZone(name="A")
        b = edm.BiddingZone(name="B")
        icx = edm.grid.Interconnection(name="X", from_element=a, to_element=b)
        assert isinstance(icx.from_element, edm.Reference)
        assert isinstance(icx.to_element, edm.Reference)
        assert icx.from_element.id == a.id
        assert icx.to_element.id == b.id
