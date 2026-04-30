"""Path-based cross-tree references.

A ``Reference[T]`` points to another Element by its position in the tree
(e.g. ``"Nordic/SE4"``) rather than by Python identity. The reference starts
as a path string and is resolved to an Element object once the tree is loaded.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from energydatamodel.element import Element


T = TypeVar("T", bound="Element")


class UnresolvedReferenceError(LookupError):
    """Raised when a Reference can't be resolved against a tree."""


class Reference(Generic[T]):
    """Typed marker for a cross-tree reference to another Element.

    Stores one of:

    * a slash-joined ``str`` path (legacy form)
    * a ``tuple[str, ...]`` path (preserves names containing slashes)
    * an :class:`Element` object (resolved form)

    Used on fields like ``Edge.from_entity`` / ``Edge.to_entity``.
    """

    __slots__ = ("_target",)

    def __init__(self, target: str | tuple[str, ...] | Element):
        if isinstance(target, list):
            target = tuple(target)
        self._target = target

    # -----------------------------------------------------------------
    def is_resolved(self) -> bool:
        return not isinstance(self._target, (str, tuple))

    @property
    def target(self) -> str | tuple[str, ...] | Element:
        return self._target

    def get(self) -> Element:
        """Return the resolved Element. Raises if still a path."""
        if isinstance(self._target, (str, tuple)):
            raise UnresolvedReferenceError(f"Reference to {self._target!r} has not been resolved.")
        return self._target

    # -----------------------------------------------------------------
    def resolve(self, root: Element) -> Element:
        """Resolve the reference against ``root``. Idempotent."""
        if not isinstance(self._target, (str, tuple)):
            return self._target
        obj = _lookup_by_path(root, self._target)
        if obj is None:
            raise UnresolvedReferenceError(
                f"Reference {self._target!r} does not resolve against {type(root).__name__}"
                f"({getattr(root, 'name', None)!r})"
            )
        self._target = obj
        return obj

    def path(self, root: Element) -> str:
        """Canonical path from ``root`` to the target.

        Returns the same canonical full path whether ``self`` holds a string
        path, a tuple path, or a resolved Element. Does not mutate ``self``.
        Raises ``UnresolvedReferenceError`` if the target is not reachable
        from ``root``.
        """
        return "/".join(self.path_tuple(root))

    def path_tuple(self, root: Element) -> tuple[str, ...]:
        """Canonical path from ``root`` to the target as a tuple of names.

        Same semantics as :meth:`path` but returns ``tuple[str, ...]`` rather
        than a slash-joined string. Use this where names may contain slashes
        or other punctuation that would be ambiguous in a string-encoded path.
        """
        if isinstance(self._target, (str, tuple)):
            obj = _lookup_by_path(root, self._target)
            if obj is None:
                raise UnresolvedReferenceError(
                    f"Reference {self._target!r} does not resolve against "
                    f"{type(root).__name__}({getattr(root, 'name', None)!r})"
                )
        else:
            obj = self._target
        parts = _path_to_parts(root, obj)
        if parts is None:
            raise UnresolvedReferenceError(
                f"Referenced entity {getattr(obj, 'name', obj)!r} "
                f"is not reachable from root {getattr(root, 'name', root)!r}."
            )
        return tuple(parts)

    # -----------------------------------------------------------------
    def __repr__(self):
        if isinstance(self._target, (str, tuple)):
            return f"Reference({self._target!r})"
        name = getattr(self._target, "name", None)
        return f"Reference(<{type(self._target).__name__}({name!r})>)"

    def __eq__(self, other):
        """Equality for References.

        Resolved targets compare by **identity** (``is``), matching the id-based
        hash so the Python hash/equality contract holds when References are used
        as ``set`` or ``dict`` keys. Unresolved path targets (string or tuple)
        compare by value. A resolved and an unresolved reference are never equal.
        """
        if not isinstance(other, Reference):
            return NotImplemented
        self_is_path = isinstance(self._target, (str, tuple))
        other_is_path = isinstance(other._target, (str, tuple))
        if self_is_path and other_is_path:
            return self._target == other._target
        if self_is_path or other_is_path:
            return False
        return self._target is other._target

    def __hash__(self):
        if isinstance(self._target, (str, tuple)):
            return hash(("Reference", self._target))
        return hash(("Reference", id(self._target)))


# ---------------------------------------------------------------------
# tree lookup helpers
# ---------------------------------------------------------------------


def _lookup_by_path(root: Element, path: str | tuple[str, ...]) -> Element | None:
    """Resolve a path by walking ``name``s.

    Accepts either a slash-separated string (legacy) or a tuple of name
    parts. Tuple form is preferred when names may contain slashes.
    """
    if isinstance(path, str):
        parts: list[str] = [p for p in path.split("/") if p]
    else:
        parts = [p for p in path if p]
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


def _path_to(root: Element, target: Element) -> str | None:
    """Compute path from root → target, return None if target is not in the tree."""
    parts = _path_to_parts(root, target)
    if parts is None:
        return None
    return "/".join(parts)


def _path_to_parts(root: Element, target: Element) -> list[str] | None:
    """Compute path from root → target as a list of names. ``None`` if not in tree."""
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
        return list(trail)
    return None
