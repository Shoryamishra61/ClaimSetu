"""API package: HTTP and WebSocket surface.

Depends on ``app.services``; never the other way round. Nothing in ``app.domain``
imports from here, which is what keeps the invariants testable without an HTTP
client.
"""
