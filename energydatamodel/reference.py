"""Path-based cross-tree references.

A ``Reference[T]`` points to another Entity by its position in the tree
(e.g. ``"Nordic/SE4"``) rather than by Python identity. The reference starts
as a path string and is resolved to an Entity object once the tree is loaded.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, Union

if TYPE_CHECKING:
    from energydatamodel.entity import Entity


T = TypeVar("T", bound="Entity")


class UnresolvedReferenceError(LookupError):
    """Raised when a Reference can't be resolved against a tree."""


class Reference(Generic[T]):
    """Typed marker for a cross-tree reference to another Entity.

    Stores either a ``str`` path (pre-resolve) or an Entity object (post-resolve).
    Used on fields like ``Edge.from_entity`` / ``Edge.to_entity``.
    """

    __slots__ = ("_target",)

    def __init__(self, target: Union[str, "Entity"]):
        self._target = target

    # -----------------------------------------------------------------
    def is_resolved(self) -> bool:
        return not isinstance(self._target, str)

    @property
    def target(self) -> Union[str, "Entity"]:
        return self._target

    def get(self) -> "Entity":
        """Return the resolved Entity. Raises if still a path string."""
        if isinstance(self._target, str):
            raise UnresolvedReferenceError(
                f"Reference to {self._target!r} has not been resolved."
            )
        return self._target

    # -----------------------------------------------------------------
    def resolve(self, root: "Entity") -> "Entity":
        """Resolve the reference against ``root``. Idempotent."""
        if not isinstance(self._target, str):
            return self._target
        obj = _lookup_by_path(root, self._target)
        if obj is None:
            raise UnresolvedReferenceError(
                f"Reference {self._target!r} does not resolve against {type(root).__name__}"
                f"({getattr(root, 'name', None)!r})"
            )
        self._target = obj
        return obj

    def path(self, root: "Entity") -> str:
        """Canonical path from ``root`` to the target.

        Returns the same canonical full path whether ``self`` holds a string
        path or a resolved Entity. Does not mutate ``self``. Raises
        ``UnresolvedReferenceError`` if the target is not reachable from ``root``.
        """
        if isinstance(self._target, str):
            obj = _lookup_by_path(root, self._target)
            if obj is None:
                raise UnresolvedReferenceError(
                    f"Reference {self._target!r} does not resolve against "
                    f"{type(root).__name__}({getattr(root, 'name', None)!r})"
                )
        else:
            obj = self._target
        p = _path_to(root, obj)
        if p is None:
            raise UnresolvedReferenceError(
                f"Referenced entity {getattr(obj, 'name', obj)!r} "
                f"is not reachable from root {getattr(root, 'name', root)!r}."
            )
        return p

    # -----------------------------------------------------------------
    def __repr__(self):
        if isinstance(self._target, str):
            return f"Reference({self._target!r})"
        name = getattr(self._target, "name", None)
        return f"Reference(<{type(self._target).__name__}({name!r})>)"

    def __eq__(self, other):
        """Equality for References.

        Resolved targets compare by **identity** (``is``), matching the id-based
        hash so the Python hash/equality contract holds when References are used
        as ``set`` or ``dict`` keys. Unresolved (string-path) targets use string
        equality. A resolved and an unresolved reference are never equal.
        """
        if not isinstance(other, Reference):
            return NotImplemented
        self_is_str = isinstance(self._target, str)
        other_is_str = isinstance(other._target, str)
        if self_is_str and other_is_str:
            return self._target == other._target
        if self_is_str or other_is_str:
            return False
        return self._target is other._target

    def __hash__(self):
        if isinstance(self._target, str):
            return hash(("Reference", self._target))
        return hash(("Reference", id(self._target)))


# ---------------------------------------------------------------------
# tree lookup helpers
# ---------------------------------------------------------------------


def _lookup_by_path(root: "Entity", path: str) -> "Entity | None":
    """Resolve a slash-separated path like ``"Nordic/SE4"`` by walking ``name``s."""
    parts = [p for p in path.split("/") if p]
    if not parts:
        return None
    # Accept either path with or without the root's own name prepended.
    if getattr(root, "name", None) == parts[0]:
        parts = parts[1:]
    node = root
    for part in parts:
        found = None
        for child in node.children():
            if getattr(child, "name", None) == part:
                found = child
                break
        if found is None:
            return None
        node = found
    return node


def _path_to(root: "Entity", target: "Entity") -> "str | None":
    """Compute path from root → target, return None if target is not in the tree."""
    trail: list[str] = []

    def walk(node) -> bool:
        trail.append(getattr(node, "name", None) or type(node).__name__)
        if node is target:
            return True
        for child in node.children():
            if walk(child):
                return True
        trail.pop()
        return False

    if walk(root):
        return "/".join(trail)
    return None
