References
=======================

Cross-tree references — ``Reference``, ``Index``, and ``build_index`` —
let one ``Element`` point at another by ``uuid`` without holding a hard
Python reference. Useful for grid topology (an ``Edge`` referencing
endpoints in a different subtree) and for round-tripping JSON without
duplicating nested objects.

.. automodule:: energydatamodel.reference
   :members:
   :undoc-members:
   :show-inheritance:
