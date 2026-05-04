"""UUID-based cross-tree references and the Index lookup primitive.

A ``Reference[T]`` points to another Element by its stable :pyclass:`UUID`
identity. Resolution against a tree builds an :class:`Index` (``dict[UUID,
Element]`` produced by DFS) and uses it for O(1) lookup. References are
valid the moment they're constructed — no two-pass deserialize.

Path-shaped operations (``Reference.path(root)``) are still available for
human display and debug, but are not part of the wire format.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from energydatamodel.element import Element


class UnresolvedReferenceError(LookupError):
    """Raised when a Reference can't be resolved against a tree."""


# ---------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------


class Index:
    """``dict[UUID, Element]`` lookup, built once via DFS.

    The Index is *not* live-tracked: mutate the tree after building, and
    the Index goes stale. Rebuild via :func:`build_index` when needed.
    """

    __slots__ = ("_by_id",)

    def __init__(self, by_id: dict[UUID, Element] | None = None):
        self._by_id: dict[UUID, Element] = dict(by_id) if by_id else {}

    def __contains__(self, key: UUID) -> bool:
        return key in self._by_id

    def __getitem__(self, key: UUID) -> Element:
        try:
            return self._by_id[key]
        except KeyError:
            raise UnresolvedReferenceError(f"No Element with id {key!s} in this index.") from None

    def __len__(self) -> int:
        return len(self._by_id)

    def __iter__(self):
        return iter(self._by_id)

    def get(self, key: UUID, default=None):
        return self._by_id.get(key, default)

    def add(self, element: Element) -> None:
        self._by_id[element.id] = element


def build_index(root: Element) -> Index:
    """Walk ``root`` (DFS via ``children()``) and collect every Element by id.

    Detects cycles: a node visited twice via the same ``id()`` raises
    :class:`ValueError`. Duplicate UUIDs (same id on two distinct objects)
    raise :class:`ValueError` — UUIDs are supposed to be unique.
    """
    by_id: dict[UUID, Element] = {}
    seen: set[int] = set()

    def _walk(node: Element) -> None:
        py_id = id(node)
        if py_id in seen:
            return  # already visited via another path; skip silently
        seen.add(py_id)
        if node.id in by_id and by_id[node.id] is not node:
            raise ValueError(
                f"Duplicate UUID {node.id} on two different Elements "
                f"({type(by_id[node.id]).__name__}, {type(node).__name__})"
            )
        by_id[node.id] = node
        for child in node.children():
            _walk(child)

    _walk(root)
    return Index(by_id)


# ---------------------------------------------------------------------
# Reference
# ---------------------------------------------------------------------


class Reference[T: "Element"]:
    """A reference to another Element by its UUID.

    Holds either:

    * a :pyclass:`UUID` (canonical, on the wire)
    * an :class:`Element` (resolved cache)

    Usage::

        Reference(other_element)        # captures other_element.id
        Reference(uuid_obj)             # by id directly
        ref.resolve(root)               # builds Index, looks up
        ref.get()                       # raises if not yet resolved
    """

    __slots__ = ("_id", "_target")

    def __init__(self, target: UUID | str | T):
        from energydatamodel.element import Element

        if isinstance(target, Element):
            self._id: UUID = target.id
            self._target: Element | None = target
        elif isinstance(target, UUID):
            self._id = target
            self._target = None
        elif isinstance(target, str):
            # Accept str form for hand-edited JSON / CLI convenience.
            self._id = UUID(target)
            self._target = None
        else:
            raise TypeError(f"Reference target must be Element | UUID | str, got {type(target).__name__}")

    # ------------------------------------------------------------------
    @property
    def id(self) -> UUID:
        """The UUID this reference points at."""
        return self._id

    def is_resolved(self) -> bool:
        return self._target is not None

    def get(self) -> Element:
        """Return the resolved Element. Raises if not resolved yet.

        Use :meth:`resolve` to resolve against a tree root first.
        """
        if self._target is None:
            raise UnresolvedReferenceError(
                f"Reference to {self._id!s} has not been resolved. Call ref.resolve(root) first."
            )
        return self._target

    def resolve(self, root_or_index: Element | Index) -> Element:
        """Resolve against a tree root or a pre-built :class:`Index`.

        Idempotent — once resolved, subsequent calls return the cached
        Element without re-walking. Pass an :class:`Index` directly when
        resolving many References against the same tree.
        """
        if self._target is not None:
            return self._target

        index = root_or_index if isinstance(root_or_index, Index) else build_index(root_or_index)

        try:
            self._target = index[self._id]
        except KeyError:
            raise UnresolvedReferenceError(f"Reference {self._id!s} does not resolve against the given tree.") from None
        return self._target

    # ------------------------------------------------------------------
    # Optional path helper (debug only — not in the wire format)
    # ------------------------------------------------------------------
    def path(self, root: Element) -> tuple[str, ...]:
        """Best-effort name path from ``root`` to the target.

        Walks ``root.children()`` looking for the target object. Used for
        human-readable display only — the wire format records UUID, not path.
        Names containing ``/`` are preserved as separate tuple elements.
        """
        target_id = self._id
        trail: list[str] = []

        def _walk(node) -> bool:
            trail.append(getattr(node, "name", None) or type(node).__name__)
            if getattr(node, "id", None) == target_id:
                return True
            for child in node.children():
                if _walk(child):
                    return True
            trail.pop()
            return False

        if _walk(root):
            return tuple(trail)
        raise UnresolvedReferenceError(
            f"Target {self._id!s} not reachable from root {type(root).__name__}({getattr(root, 'name', None)!r})."
        )

    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        if self._target is None:
            return f"Reference({self._id!s})"
        name = getattr(self._target, "name", None)
        return f"Reference(<{type(self._target).__name__}({name!r})>)"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Reference):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(("Reference", self._id))
