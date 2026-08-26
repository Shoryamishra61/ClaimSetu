"""Simulated adapters -- the only things in this codebase shaped like a government
system, and the only things that must never be mistaken for one.

Nothing here performs I/O beyond reading local fixture JSON. There is no HTTP
client, no socket, and no configuration that could point any of these at a real
host. That absence is the control behind claim "never call a live government
system" and is asserted by ``tests/test_no_live_integration.py``.
"""
