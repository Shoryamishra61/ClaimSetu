"""Persistence layer.

Two rules, both enforced by ``tests/test_layering.py``:

1.  **Only ``app.services`` may open a transaction.** ``db.read()`` and
    ``db.write()`` appear nowhere else. ``app.api`` and ``app.main`` do import from
    this package -- for row *types* (``repo.AuditEventRow``), pure helpers
    (``repo.verify_chain``) and exception classes -- and that is allowed precisely
    because none of those touch a connection. No function in ``app.api`` takes a
    ``sqlite3.Connection``.
2.  **Nothing in ``app.domain`` may import this package**, because the domain must
    stay a pure, testable core with no storage dependency. This package depends on
    ``app.domain`` and ``app.clock``, and on nothing else in the application.
"""

from .connection import Database

__all__ = ["Database"]
