"""Application services: the only layer that may open a database transaction.

Layering rules enforced by ``tests/test_layering.py``:

    main  ->  api  ->  services  ->  domain
                                \\->  adapters
                                \\->  db

``app.api`` also names types from ``app.db`` and ``app.adapters`` directly -- a row
class to annotate a serialiser, a reason-code table to translate. That is allowed
because none of it touches a connection or performs a lookup: the transaction
boundary stays here, and no function in ``app.api`` takes a ``sqlite3.Connection``.

The two directions that are absolute:

*   ``app.domain`` imports nothing else in the application -- not ``app.services``,
    ``app.db``, ``app.adapters``, ``app.api``, ``app.clock`` or ``app.errors``. That
    is what keeps the state machine, the policy engine and the canonical payload
    testable as pure functions, and it is why the invariant tests can assert product
    rules without standing up an application.
*   ``app.adapters`` likewise imports nothing else in the application. The simulated
    government boundary knows nothing about the product wrapped around it, so it
    cannot acquire product behaviour by accident.
"""
