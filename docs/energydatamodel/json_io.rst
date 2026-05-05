JSON I/O
=======================

Lossless JSON round-trip for any registered ``Element`` subclass.
``Element.__init_subclass__`` auto-registers subclasses, so user-defined
node/edge types serialize without any explicit decorator. Plain value
dataclasses (non-``Element``) must register themselves via
:func:`register_value_type`.

.. automodule:: energydatamodel.json_io
   :members:
     element_to_json,
     element_from_json,
     element_to_storage_dict,
     to_json_str,
     from_json_str,
     register_element,
     register_value_type,
     register_builtin_elements
   :undoc-members:
   :show-inheritance:
