"""JSON serialization for Element trees.

Wire format: each element → ``{"__type__": "ClassName", ...fields}``. Lists
of Elements become nested arrays of such dicts. ``Reference`` fields become
path strings. Enums become their string values. Value-type dataclasses
(``Location``, ``Carrier``, ...) use the same ``__type__`` tag.

The reserved ``__type__`` key (double-underscore prefix) avoids collisions
with dataclass fields — classes like :class:`Building` and :class:`House`
have a ``type`` field of their own, which must survive round-trip.

``from_json`` is a two-pass walk:

1. Instantiate: dispatch each ``"__type__"`` to its class via the registry,
   instantiate with string-path ``Reference``s.
2. Resolve: walk the tree once more, resolve every Reference against the root.
"""

from __future__ import annotations

import dataclasses
import datetime
import json as json_module
import typing
from enum import Enum
from functools import cache
from typing import Any, get_args, get_origin
from zoneinfo import ZoneInfo

from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry
from timedatamodel import DataType, Frequency, TimeSeriesDescriptor, TimeSeriesType

from energydatamodel.element import Element
from energydatamodel.reference import Reference

# ---------------------------------------------------------------------
# Registries
# ---------------------------------------------------------------------


_REGISTRY: dict[str, type[Element]] = {}
_VALUE_REGISTRY: dict[str, type] = {}


def register_element(cls: type[Element]) -> type[Element]:
    """Register an Element subclass under its class name for JSON dispatch."""
    name = cls.__name__
    if name in _REGISTRY and _REGISTRY[name] is not cls:
        raise ValueError(f"register_element: duplicate name {name!r} (existing={_REGISTRY[name]!r}, new={cls!r})")
    _REGISTRY[name] = cls
    return cls


def register_value_type(cls: type) -> type:
    """Register a non-Element value dataclass (Location, Carrier, ...) for JSON dispatch.

    Value types carry a ``__type__`` tag on the wire and are instantiated by
    class-name lookup on load. Analogous to ``register_element`` but without the
    Element inheritance requirement.
    """
    name = cls.__name__
    if name in _VALUE_REGISTRY and _VALUE_REGISTRY[name] is not cls:
        raise ValueError(
            f"register_value_type: duplicate name {name!r} (existing={_VALUE_REGISTRY[name]!r}, new={cls!r})"
        )
    _VALUE_REGISTRY[name] = cls
    return cls


def get_registry() -> dict[str, type[Element]]:
    return dict(_REGISTRY)


# ---------------------------------------------------------------------
# Serialization (Element → dict)
# ---------------------------------------------------------------------


def _serialize_value(
    value: Any,
    *,
    include_ids: bool,
    root: Element,
    exclude_fields: set | None = None,
) -> Any:
    if value is None:
        return None
    if isinstance(value, Element):
        return _element_to_dict(value, include_ids=include_ids, root=root, exclude_fields=exclude_fields)
    if isinstance(value, Reference):
        # Always emit the canonical full path from ``root``, regardless of whether
        # the Reference's internal target is still a string or a resolved Element.
        # ``Reference.path`` raises ``UnresolvedReferenceError`` if unreachable.
        return {"__ref__": value.path(root)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, datetime.tzinfo):
        name = getattr(value, "key", None) or str(value)
        return {"__tz__": name}
    if isinstance(value, BaseGeometry):
        # Shapely geometry → GeoJSON dict tagged with ``__geometry__`` for dispatch on load.
        return {"__geometry__": True, **mapping(value)}
    if isinstance(value, TimeSeriesDescriptor):
        return _descriptor_to_dict(value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _plain_dataclass_to_dict(value, include_ids=include_ids, root=root)
    if isinstance(value, list):
        return [_serialize_value(v, include_ids=include_ids, root=root, exclude_fields=exclude_fields) for v in value]
    if isinstance(value, tuple):
        return {
            "__tuple__": [
                _serialize_value(v, include_ids=include_ids, root=root, exclude_fields=exclude_fields) for v in value
            ]
        }
    if isinstance(value, dict):
        return {
            k: _serialize_value(v, include_ids=include_ids, root=root, exclude_fields=exclude_fields)
            for k, v in value.items()
        }
    if isinstance(value, (str, int, float, bool)):
        return value
    # Fallback: string repr. Avoids silent data loss for unknown types.
    return repr(value)


def _descriptor_to_dict(desc: TimeSeriesDescriptor) -> dict:
    out: dict = {"__type__": "TimeSeriesDescriptor"}
    for f in dataclasses.fields(desc):
        v = getattr(desc, f.name)
        if isinstance(v, Enum):
            out[f.name] = v.value
        else:
            out[f.name] = v
    return out


def _plain_dataclass_to_dict(obj, *, include_ids: bool, root: Element) -> dict:
    out: dict = {"__type__": type(obj).__name__}
    for f in dataclasses.fields(obj):
        v = getattr(obj, f.name)
        out[f.name] = _serialize_value(v, include_ids=include_ids, root=root)
    return out


def _element_to_dict(
    element: Element,
    *,
    include_ids: bool,
    root: Element,
    exclude_fields: set | None = None,
) -> dict:
    out: dict = {"__type__": type(element).__name__}
    for f in dataclasses.fields(element):
        name = f.name
        if name == "_id" and not include_ids:
            continue
        if exclude_fields and name in exclude_fields:
            continue
        value = getattr(element, name)
        if value is None:
            continue
        if isinstance(value, (list, dict)) and not value:
            continue
        out[name] = _serialize_value(value, include_ids=include_ids, root=root, exclude_fields=exclude_fields)
    return out


def element_to_json(
    element: Element,
    *,
    include_ids: bool = False,
    exclude_fields: set | None = None,
) -> dict:
    """Public: serialize an Element (and its subtree) to a JSON-compatible dict.

    Resolved ``Reference`` fields are emitted as full paths from ``element``
    (the serialization root), so same-name collisions in different branches
    round-trip deterministically. Raises ``UnresolvedReferenceError`` if a
    resolved reference points outside ``element``'s subtree.

    Args:
        element: The Element to serialize.
        include_ids: If True, emit ``_id`` fields (omitted by default).
        exclude_fields: Set of field names to skip when serializing. Applied
            recursively to nested Elements (e.g. passing ``{"members"}``
            produces a flat, children-free dict). See
            :func:`element_to_storage_dict` for the canonical flat-row form.
    """
    return _element_to_dict(element, include_ids=include_ids, root=element, exclude_fields=exclude_fields)


def to_json_str(
    element: Element,
    *,
    include_ids: bool = False,
    indent: int | None = None,
    exclude_fields: set | None = None,
) -> str:
    """Convenience: return a JSON string instead of a dict."""
    return json_module.dumps(
        element_to_json(element, include_ids=include_ids, exclude_fields=exclude_fields),
        indent=indent,
    )


def element_to_storage_dict(element: Element, *, extra_excludes: set | None = None) -> dict:
    """Flat-row serialization: element's own fields only, children excluded.

    Suitable for persistence layers that store tree structure separately
    (e.g. via ``parent_id`` columns rather than nested JSON). ``_id`` and any
    fields in the element's ``_CHILDREN_FIELDS`` are excluded automatically;
    add more via ``extra_excludes`` (e.g. ``{"from_entity", "to_entity"}``
    for edges whose endpoints are stored as FK columns).
    """
    excludes = set(element._CHILDREN_FIELDS)
    if extra_excludes:
        excludes = excludes | extra_excludes
    return element_to_json(element, exclude_fields=excludes)


# ---------------------------------------------------------------------
# Deserialization (dict → Element)
# ---------------------------------------------------------------------


def element_from_json(data: dict, *, expected_type: type[Element] | None = None) -> Element:
    """Public: deserialize a JSON-compatible dict into an Element tree.

    Performs the two-pass walk (instantiate + resolve references).
    """
    root = _instantiate(data)
    if expected_type is not None and expected_type is not Element:
        if not isinstance(root, expected_type):
            raise TypeError(f"Expected {expected_type.__name__}, got {type(root).__name__}")
    _resolve_references(root, root=root)
    return root


def from_json_str(text: str, *, expected_type: type[Element] | None = None) -> Element:
    return element_from_json(json_module.loads(text), expected_type=expected_type)


# ----- pass 1: instantiate -----


def _instantiate(data: Any) -> Any:
    # Tagged-dict markers: the double-underscore keys are reserved for
    # serializer metadata and cannot collide with dataclass field names.
    if isinstance(data, dict) and "__tuple__" in data:
        return tuple(_instantiate(v) for v in data["__tuple__"])
    if isinstance(data, dict) and data.get("__geometry__") is True:
        payload = {k: v for k, v in data.items() if k != "__geometry__"}
        return shape(payload)
    if isinstance(data, dict) and data.get("__type__") == "TimeSeriesDescriptor":
        return _descriptor_from_dict(data)
    if isinstance(data, dict) and data.get("__type__") in _VALUE_REGISTRY:
        cls = _VALUE_REGISTRY[data["__type__"]]
        kwargs = {k: _instantiate(v) for k, v in data.items() if k != "__type__"}
        return cls(**kwargs)
    if isinstance(data, dict) and "__tz__" in data:
        return ZoneInfo(data["__tz__"])
    if isinstance(data, dict) and "__ref__" in data:
        return Reference(data["__ref__"])
    if isinstance(data, dict) and data.get("__type__") in _REGISTRY:
        cls = _REGISTRY[data["__type__"]]
        kwargs = _build_kwargs(cls, data)
        return cls(**kwargs)
    if isinstance(data, dict) and "__type__" in data:
        # Tagged but unknown — fail loudly.
        raise ValueError(f"Unknown Element type {data['__type__']!r}. Known types: {sorted(_REGISTRY)}")
    if isinstance(data, list):
        return [_instantiate(v) for v in data]
    return data


@cache
def _resolved_type_hints(cls: type) -> dict[str, Any]:
    """Resolve string annotations on a dataclass to concrete types (once per class)."""
    try:
        return typing.get_type_hints(cls)
    except Exception:
        return {}


def _build_kwargs(cls: type[Element], data: dict) -> dict:
    kwargs: dict = {}
    field_map = {f.name: f for f in dataclasses.fields(cls)}
    hints = _resolved_type_hints(cls)
    for key, raw in data.items():
        if key == "__type__":
            continue
        if key not in field_map:
            continue  # unknown field — ignore (forward-compat)
        f = field_map[key]
        # Prefer resolved type hint (handles ``from __future__ import annotations``).
        field_type = hints.get(key, f.type)
        kwargs[key] = _instantiate_for_field(field_type, raw)
    return kwargs


def _instantiate_for_field(field_type: Any, raw: Any) -> Any:
    """Convert a raw JSON value based on the dataclass field type hint."""
    # Resolve enum targets specifically; strings on enum-typed fields → enum member.
    target_types = _unwrap_optional(field_type)
    for t in target_types:
        if isinstance(t, type) and issubclass(t, Enum) and isinstance(raw, str):
            try:
                return t(raw)
            except ValueError:
                pass
        if isinstance(t, type) and t is datetime.date and isinstance(raw, str):
            try:
                return datetime.date.fromisoformat(raw)
            except ValueError:
                pass
        if isinstance(t, type) and t is datetime.datetime and isinstance(raw, str):
            try:
                return datetime.datetime.fromisoformat(raw)
            except ValueError:
                pass
    # Dicts / lists → instantiate recursively.
    return _instantiate(raw)


def _unwrap_optional(tp: Any) -> list:
    """Return the set of concrete types inside an Optional/Union/forward-ref."""
    result: list = []
    # Optional[X] == Union[X, None]
    origin = get_origin(tp)
    if origin is None:
        if isinstance(tp, type):
            result.append(tp)
        return result
    args = get_args(tp)
    for a in args:
        if a is type(None):
            continue
        if isinstance(a, type):
            result.append(a)
    return result


def _descriptor_from_dict(d: dict) -> TimeSeriesDescriptor:
    kwargs = {}
    for k, v in d.items():
        if k == "__type__":
            continue
        if k == "data_type" and isinstance(v, str):
            kwargs[k] = DataType(v)
        elif k == "timeseries_type" and isinstance(v, str):
            kwargs[k] = TimeSeriesType(v)
        elif k == "frequency" and isinstance(v, str):
            kwargs[k] = Frequency(v)
        else:
            kwargs[k] = v
    return TimeSeriesDescriptor(**kwargs)


# ----- pass 2: resolve references -----


def _resolve_references(node: Element, *, root: Element) -> None:
    for f in dataclasses.fields(node):
        v = getattr(node, f.name)
        if isinstance(v, Reference):
            v.resolve(root)
    for child in node.children():
        _resolve_references(child, root=root)


# ---------------------------------------------------------------------
# Convenience: register every currently-known Element subclass.
# Called from ``__init__`` after all modules have loaded.
# ---------------------------------------------------------------------


def register_builtin_elements() -> None:
    """Register all Element subclasses reachable via __subclasses__ at call time.

    Use as a fallback so callers don't have to decorate every class manually —
    the explicit ``@register_element`` decorator remains the canonical path.
    Walks the whole Element subtree (Node, Edge, Asset, Collection, and all
    their descendants).
    """

    def _walk(cls: type[Element]):
        for sub in cls.__subclasses__():
            try:
                register_element(sub)
            except ValueError:
                pass  # already registered with same class object
            _walk(sub)

    _walk(Element)
