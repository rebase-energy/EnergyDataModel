"""JSON serialization for Entity trees.

Wire format: each entity → ``{"type": "ClassName", ...fields}``. Lists of
Entities become nested arrays of such dicts. ``Reference`` fields become path
strings. Enums become their string values. Dataclass value types (e.g.
``Location``, ``Carrier``) are serialized as nested dicts without a ``type``
tag (they're not Entity subclasses and are round-tripped by field-type
inspection on the receiving side).

``from_json`` is a two-pass walk:

1. Instantiate: dispatch each ``"type"`` to its class via the registry,
   instantiate with string-path ``Reference``s.
2. Resolve: walk the tree once more, resolve every Reference against the root.
"""

from __future__ import annotations

import dataclasses
import datetime
import json as json_module
from enum import Enum
from typing import Any, Dict, List, Optional, Type, get_args, get_origin

from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry
from timedatamodel import DataType, Frequency, TimeSeriesDescriptor, TimeSeriesType

from energydatamodel.entity import Entity
from energydatamodel.reference import Reference, UnresolvedReferenceError


# ---------------------------------------------------------------------
# Registries
# ---------------------------------------------------------------------


_REGISTRY: Dict[str, Type[Entity]] = {}
_VALUE_REGISTRY: Dict[str, type] = {}


def register_entity(cls: Type[Entity]) -> Type[Entity]:
    """Register an Entity subclass under its class name for JSON dispatch."""
    name = cls.__name__
    if name in _REGISTRY and _REGISTRY[name] is not cls:
        raise ValueError(
            f"register_entity: duplicate name {name!r} "
            f"(existing={_REGISTRY[name]!r}, new={cls!r})"
        )
    _REGISTRY[name] = cls
    return cls


def register_value_type(cls: type) -> type:
    """Register a non-Entity value dataclass (Location, Carrier, ...) for JSON dispatch.

    Value types carry a ``__type__`` tag on the wire and are instantiated by
    class-name lookup on load. Analogous to ``register_entity`` but without the
    Entity inheritance requirement.
    """
    name = cls.__name__
    if name in _VALUE_REGISTRY and _VALUE_REGISTRY[name] is not cls:
        raise ValueError(
            f"register_value_type: duplicate name {name!r} "
            f"(existing={_VALUE_REGISTRY[name]!r}, new={cls!r})"
        )
    _VALUE_REGISTRY[name] = cls
    return cls


def get_registry() -> Dict[str, Type[Entity]]:
    return dict(_REGISTRY)


# ---------------------------------------------------------------------
# Serialization (Entity → dict)
# ---------------------------------------------------------------------


def _serialize_value(value: Any, *, include_ids: bool, root: Entity) -> Any:
    if value is None:
        return None
    if isinstance(value, Entity):
        return _entity_to_dict(value, include_ids=include_ids, root=root)
    if isinstance(value, Reference):
        # Always emit the canonical full path from ``root``, regardless of whether
        # the Reference's internal target is still a string or a resolved Entity.
        # ``Reference.path`` raises ``UnresolvedReferenceError`` if unreachable.
        return {"__ref__": value.path(root)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime.tzinfo):
        # pytz timezones expose ``zone``; stdlib zoneinfo uses ``key``. Fall back to str().
        return getattr(value, "zone", None) or getattr(value, "key", None) or str(value)
    if isinstance(value, BaseGeometry):
        # Shapely geometry → GeoJSON dict tagged with ``__geometry__`` for dispatch on load.
        return {"__geometry__": True, **mapping(value)}
    if isinstance(value, TimeSeriesDescriptor):
        return _descriptor_to_dict(value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _plain_dataclass_to_dict(value, include_ids=include_ids, root=root)
    if isinstance(value, list):
        return [_serialize_value(v, include_ids=include_ids, root=root) for v in value]
    if isinstance(value, tuple):
        return {"__tuple__": [_serialize_value(v, include_ids=include_ids, root=root) for v in value]}
    if isinstance(value, dict):
        return {k: _serialize_value(v, include_ids=include_ids, root=root) for k, v in value.items()}
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


def _plain_dataclass_to_dict(obj, *, include_ids: bool, root: Entity) -> dict:
    out: dict = {"__type__": type(obj).__name__}
    for f in dataclasses.fields(obj):
        v = getattr(obj, f.name)
        out[f.name] = _serialize_value(v, include_ids=include_ids, root=root)
    return out


def _entity_to_dict(entity: Entity, *, include_ids: bool, root: Entity) -> dict:
    out: dict = {"type": type(entity).__name__}
    for f in dataclasses.fields(entity):
        name = f.name
        if name == "_id" and not include_ids:
            continue
        value = getattr(entity, name)
        if value is None:
            continue
        if isinstance(value, list) and not value:
            continue
        out[name] = _serialize_value(value, include_ids=include_ids, root=root)
    return out


def entity_to_json(entity: Entity, *, include_ids: bool = False) -> dict:
    """Public: serialize an Entity (and its subtree) to a JSON-compatible dict.

    Resolved ``Reference`` fields are emitted as full paths from ``entity``
    (the serialization root), so same-name collisions in different branches
    round-trip deterministically. Raises ``UnresolvedReferenceError`` if a
    resolved reference points outside ``entity``'s subtree.
    """
    return _entity_to_dict(entity, include_ids=include_ids, root=entity)


def to_json_str(entity: Entity, *, include_ids: bool = False, indent: Optional[int] = None) -> str:
    """Convenience: return a JSON string instead of a dict."""
    return json_module.dumps(entity_to_json(entity, include_ids=include_ids), indent=indent)


# ---------------------------------------------------------------------
# Deserialization (dict → Entity)
# ---------------------------------------------------------------------


def entity_from_json(data: dict, *, expected_type: Optional[Type[Entity]] = None) -> Entity:
    """Public: deserialize a JSON-compatible dict into an Entity tree.

    Performs the two-pass walk (instantiate + resolve references).
    """
    root = _instantiate(data)
    if expected_type is not None and expected_type is not Entity:
        if not isinstance(root, expected_type):
            raise TypeError(
                f"Expected {expected_type.__name__}, got {type(root).__name__}"
            )
    _resolve_references(root, root=root)
    return root


def from_json_str(text: str, *, expected_type: Optional[Type[Entity]] = None) -> Entity:
    return entity_from_json(json_module.loads(text), expected_type=expected_type)


# ----- pass 1: instantiate -----


def _instantiate(data: Any) -> Any:
    # Check tagged-dict markers (more specific) before the generic ``"type"`` branch:
    # GeoJSON also uses a ``"type"`` field (e.g. ``"Polygon"``), so geometry must be
    # detected via the ``__geometry__`` tag first.
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
    if isinstance(data, dict) and "__ref__" in data:
        return Reference(data["__ref__"])
    if isinstance(data, dict) and "type" in data:
        type_name = data["type"]
        if type_name not in _REGISTRY:
            raise ValueError(
                f"Unknown Entity type {type_name!r}. Known types: {sorted(_REGISTRY)}"
            )
        cls = _REGISTRY[type_name]
        kwargs = _build_kwargs(cls, data)
        return cls(**kwargs)
    if isinstance(data, list):
        return [_instantiate(v) for v in data]
    return data


def _build_kwargs(cls: Type[Entity], data: dict) -> dict:
    kwargs: dict = {}
    field_map = {f.name: f for f in dataclasses.fields(cls)}
    for key, raw in data.items():
        if key == "type":
            continue
        if key not in field_map:
            continue  # unknown field — ignore (forward-compat)
        f = field_map[key]
        kwargs[key] = _instantiate_for_field(f.type, raw)
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


def _resolve_references(node: Entity, *, root: Entity) -> None:
    for f in dataclasses.fields(node):
        v = getattr(node, f.name)
        if isinstance(v, Reference):
            v.resolve(root)
    for child in node.children():
        _resolve_references(child, root=root)


# ---------------------------------------------------------------------
# Convenience: register every currently-known Entity subclass.
# Called from ``__init__`` after all modules have loaded.
# ---------------------------------------------------------------------


def register_builtin_entities() -> None:
    """Register all Entity subclasses reachable via __subclasses__ at call time.

    Use as a fallback so callers don't have to decorate every class manually —
    the explicit ``@register_entity`` decorator remains the canonical path.
    Walks both the Node and Edge subtrees under Entity.
    """

    def _walk(cls: Type[Entity]):
        for sub in cls.__subclasses__():
            try:
                register_entity(sub)
            except ValueError:
                pass  # already registered with same class object
            _walk(sub)

    _walk(Entity)
