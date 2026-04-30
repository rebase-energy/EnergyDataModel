"""Tests for the user-extension story: subclass auto-registration and the
``Element.extra`` ad-hoc field."""

from dataclasses import dataclass

import energydatamodel as edm
from energydatamodel.json_io import _REGISTRY


# Defined at module scope so it's registered exactly once when this test module loads.
@dataclass(repr=False, kw_only=True)
class Electrolyzer(edm.NodeAsset):
    capacity_kw: float | None = None
    efficiency: float | None = None


class TestSubclassAutoRegistration:
    def test_subclass_is_auto_registered(self):
        assert _REGISTRY["Electrolyzer"] is Electrolyzer

    def test_subclass_roundtrips_through_json(self):
        e = Electrolyzer(name="EL-1", capacity_kw=5000, efficiency=0.65)
        site = edm.Site(name="H2 Site", members=[e])

        restored = edm.Element.from_json(site.to_json())

        assert isinstance(restored, edm.Site)
        assert len(restored.members) == 1
        assert isinstance(restored.members[0], Electrolyzer)
        assert restored.members[0].name == "EL-1"
        assert restored.members[0].capacity_kw == 5000
        assert restored.members[0].efficiency == 0.65

    def test_redefining_class_overwrites_registry(self):
        # Notebook re-run scenario: redefining a class with the same name produces
        # a new class object. Last-write-wins so the new class is authoritative.
        @dataclass(repr=False, kw_only=True)
        class TempAsset(edm.NodeAsset):
            v: int = 0

        first = _REGISTRY["TempAsset"]
        assert first is TempAsset

        @dataclass(repr=False, kw_only=True)
        class TempAsset(edm.NodeAsset):  # noqa: F811 — intentional redefinition
            v: int = 0

        second = _REGISTRY["TempAsset"]
        assert second is TempAsset
        assert second is not first


class TestExtraField:
    def test_extra_defaults_to_empty_dict(self):
        e = edm.Site(name="x")
        assert e.extra == {}

    def test_extra_roundtrips_with_nested_values(self):
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

    def test_extra_excluded_from_to_properties(self):
        e = Electrolyzer(name="EL-1", capacity_kw=5000, extra={"owner": "Acme"})
        props = e.to_properties()
        assert "extra" not in props
        assert "capacity_kw" in props

    def test_extra_on_subclass_roundtrips(self):
        e = Electrolyzer(name="EL-1", capacity_kw=5000, extra={"site_code": "H2-A"})
        restored = edm.Element.from_json(e.to_json())
        assert isinstance(restored, Electrolyzer)
        assert restored.extra == {"site_code": "H2-A"}
