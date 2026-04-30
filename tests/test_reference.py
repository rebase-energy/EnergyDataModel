"""Tests for Reference[T] — path-based cross-tree references."""

import energydatamodel as edm
import pytest
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


class TestReferenceTuple:
    """Tuple-form references: identity-as-path that's safe for names with /."""

    def test_construct_from_tuple(self):
        ref = edm.Reference(("Nordic", "SE4"))
        assert ref.target == ("Nordic", "SE4")
        assert not ref.is_resolved()

    def test_construct_from_list_normalises_to_tuple(self):
        ref = edm.Reference(["Nordic", "SE4"])
        assert ref.target == ("Nordic", "SE4")

    def test_resolve_tuple_against_tree(self):
        portfolio, se4, *_ = _make_tree()
        ref = edm.Reference(("Nordic", "SE4"))
        assert ref.resolve(portfolio) is se4

    def test_path_tuple_of_resolved(self):
        portfolio, se4, _, _ = _make_tree()
        ref = edm.Reference(se4)
        assert ref.path_tuple(portfolio) == ("Nordic", "SE4")

    def test_path_tuple_of_unresolved_string(self):
        portfolio, *_ = _make_tree()
        ref = edm.Reference("Nordic/SE4")
        assert ref.path_tuple(portfolio) == ("Nordic", "SE4")

    def test_path_tuple_of_unresolved_tuple(self):
        portfolio, *_ = _make_tree()
        ref = edm.Reference(("Nordic", "SE4"))
        assert ref.path_tuple(portfolio) == ("Nordic", "SE4")

    def test_name_with_slash_only_works_via_tuple(self):
        weird = edm.BiddingZone(name="A/B")
        portfolio = edm.Portfolio(name="P", members=[weird])
        # String-path resolution mis-parses 'A/B' as two segments → fails.
        bad = edm.Reference("P/A/B")
        with pytest.raises(UnresolvedReferenceError):
            bad.resolve(portfolio)
        # Tuple form preserves the slash literally.
        good = edm.Reference(("P", "A/B"))
        assert good.resolve(portfolio) is weird
        assert good.path_tuple(portfolio) == ("P", "A/B")
