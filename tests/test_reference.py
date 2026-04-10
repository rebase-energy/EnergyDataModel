"""Tests for Reference[T] — path-based cross-tree references."""

import pytest

import energydatamodel as edm
from energydatamodel.reference import UnresolvedReferenceError


def _make_tree():
    se4 = edm.BiddingZone(name="SE4")
    dk2 = edm.BiddingZone(name="DK2")
    icx = edm.Interconnection(
        name="SE4-DK2",
        from_entity=edm.Reference("SE4"),
        to_entity=edm.Reference("DK2"),
    )
    return edm.Portfolio(name="Nordic", members=[se4, dk2, icx]), se4, dk2, icx


class TestReference:
    def test_unresolved_initially(self):
        ref = edm.Reference("Nordic/SE4")
        assert not ref.is_resolved()
        with pytest.raises(UnresolvedReferenceError):
            ref.get()

    def test_resolve_against_tree(self):
        portfolio, se4, _, icx = _make_tree()
        icx.from_entity.resolve(portfolio)
        assert icx.from_entity.is_resolved()
        assert icx.from_entity.get() is se4

    def test_resolve_unknown_raises(self):
        portfolio, *_ = _make_tree()
        ref = edm.Reference("NotThere")
        with pytest.raises(UnresolvedReferenceError):
            ref.resolve(portfolio)

    def test_path_of_resolved(self):
        portfolio, se4, _, _ = _make_tree()
        ref = edm.Reference(se4)
        assert ref.path(portfolio) == "Nordic/SE4"

    def test_path_outside_tree_raises(self):
        portfolio, *_ = _make_tree()
        stranger = edm.BiddingZone(name="NO2")
        ref = edm.Reference(stranger)
        with pytest.raises(UnresolvedReferenceError):
            ref.path(portfolio)

    def test_nested_path(self):
        t01 = edm.WindTurbine(name="T01", capacity=3.5)
        farm = edm.WindFarm(name="Lillgrund", members=[t01])
        site = edm.Site(name="Sweden", members=[farm])
        portfolio = edm.Portfolio(name="Nordic", members=[site])
        ref = edm.Reference("Nordic/Sweden/Lillgrund/T01")
        ref.resolve(portfolio)
        assert ref.get() is t01
