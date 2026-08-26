"""Domain layer: pure logic, no I/O, no framework, no mock-adapter knowledge.

Nothing in this package may import from ``app.adapters`` or ``app.api``. That
one-way dependency is what keeps the state machine independent of the simulated
government boundary (07_ARCHITECTURE_DATA_MODEL.md section 3) and is asserted by
``tests/test_layering.py``.
"""
