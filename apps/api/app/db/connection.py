"""SQLite access with WAL journalling and explicit write transactions.

Design notes worth knowing before changing anything here:

*   **A connection per transaction.** FastAPI runs sync endpoint code in a thread
    pool, and a shared ``sqlite3.Connection`` is not safe across threads. Opening
    per transaction is cheap for SQLite and removes the whole class of
    cross-thread cursor bugs.
*   **``BEGIN IMMEDIATE`` for writes.** SQLite's default deferred transaction takes
    the write lock only at the first write, which leaves a window between a
    ``SELECT current_state`` and the ``UPDATE`` that depends on it. Every write
    transaction here takes the lock up front, which is what makes the
    compare-and-set state transition in ``repository.transition_state`` actually
    atomic rather than merely usually-correct.
*   **No in-memory mode.** ``:memory:`` is rejected because a per-transaction
    connection would silently get an empty database each time. Tests use a real
    file under ``tmp_path``, which also exercises WAL for free.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

#: Milliseconds a blocked writer waits for the lock before raising. Generous
#: because the only contention in this prototype is two parties acting at once.
BUSY_TIMEOUT_MS = 5_000


class Database:
    def __init__(self, path: str) -> None:
        if path.strip() in {":memory:", ""}:
            raise ValueError(
                "In-memory SQLite is not supported: this module opens a connection "
                "per transaction, so an in-memory database would be empty on every "
                "call. Point database_path at a file (tests: tmp_path)."
            )
        self.path = Path(path)

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(
            self.path,
            # Explicit transaction control; see the BEGIN IMMEDIATE note above.
            isolation_level=None,
            timeout=BUSY_TIMEOUT_MS / 1000,
        )
        connection.row_factory = sqlite3.Row
        # WAL is persistent per database file, but journal_mode is cheap and
        # idempotent to set, and setting it here means a fresh file is correct
        # from its first connection.
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
        return connection

    def initialise(self) -> None:
        self.apply_schema(SCHEMA_PATH)

    def apply_schema(self, schema_path: Path) -> None:
        """Apply an idempotent schema file as one atomic operation."""
        script = schema_path.read_text(encoding="utf-8")
        connection = self._connect()
        try:
            # ``sqlite3.executescript`` implicitly commits a pending transaction
            # before it runs. Starting the transaction with ``execute`` and then
            # committing afterwards therefore fails with "no transaction is
            # active" on Python's sqlite3 driver. Put the transaction control in
            # the script so schema creation is still atomic.
            connection.executescript(f"BEGIN IMMEDIATE;\n{script}\nCOMMIT;")
        except Exception:
            # A syntax/constraint failure may already have ended the transaction.
            # Guarding the rollback preserves the original, useful exception.
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    @contextmanager
    def write(self) -> Iterator[sqlite3.Connection]:
        """A serialised write transaction. Commits on success, rolls back on error."""
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
        except Exception:
            connection.execute("ROLLBACK")
            raise
        else:
            connection.execute("COMMIT")
        finally:
            connection.close()

    @contextmanager
    def read(self) -> Iterator[sqlite3.Connection]:
        """A read-only view. Under WAL this never blocks a writer."""
        connection = self._connect()
        try:
            yield connection
        finally:
            connection.close()

    def reset(self) -> None:
        """Drop all case data. Used by the demo-reset endpoint and by tests.

        Deletes from ``cases`` only and relies on ``ON DELETE CASCADE``, so adding
        a child table cannot leave orphan rows behind after a reset.
        """
        with self.write() as connection:
            connection.execute("DELETE FROM cases")
