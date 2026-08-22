-- Handover29C prototype schema.
--
-- Conventions:
--   * timestamps are ISO-8601 UTC strings ("2026-08-22T05:00:00+00:00"); the UI
--     renders IST (SRS section 11).
--   * booleans are 0/1 integers.
--   * every child table cascades from cases, so resetting demo data is one delete.
--
-- Vehicle and dealer fixtures are deliberately NOT tables. They live in
-- fixtures/*.json and are read through the registry adapters, so there is exactly
-- one source of truth for the fictional records and no chance of a seeded copy
-- drifting from it. See DECISIONS.md ADR-005.

CREATE TABLE IF NOT EXISTS cases (
    id                     TEXT    PRIMARY KEY,
    journey_type           TEXT    NOT NULL,
    current_state          TEXT    NOT NULL,
    policy_version         TEXT    NOT NULL,
    vehicle_id             TEXT,
    dealer_id              TEXT,
    -- Snapshot of the dealer status at verification time. Never trusted at
    -- submit: INV-04 requires a fresh registry lookup at that moment.
    dealer_status_at_verify TEXT,
    handover_local_time    TEXT,
    payload_hash           TEXT,
    seller_confirmed_hash  TEXT,
    dealer_confirmed_hash  TEXT,
    -- There is deliberately no acknowledgement_no column here. The acknowledgement
    -- lives on submission_attempts and nowhere else, so there is exactly one place
    -- that can say a handover was acknowledged (INV-01). A convenience copy on this
    -- row would be a second authority, and the two could disagree.
    created_at             TEXT    NOT NULL,
    updated_at             TEXT    NOT NULL
);

-- One row per declaration code the parties can set. Fixture-derived checks are
-- not stored here; they are recomputed from the registries on every evaluation so
-- a stale copy can never make a blocked case look ready.
CREATE TABLE IF NOT EXISTS declarations (
    case_id        TEXT    NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    code           TEXT    NOT NULL,
    value          INTEGER NOT NULL CHECK (value IN (0, 1)),
    source_type    TEXT    NOT NULL,
    policy_version TEXT    NOT NULL,
    actor          TEXT    NOT NULL,
    updated_at     TEXT    NOT NULL,
    PRIMARY KEY (case_id, code)
);

-- A one-time seller->dealer link. Only the hash of the code is stored, so the
-- database never holds a usable credential (SRS section 8).
CREATE TABLE IF NOT EXISTS pair_sessions (
    id                TEXT PRIMARY KEY,
    case_id           TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    token_hash        TEXT NOT NULL UNIQUE,
    expires_at        TEXT NOT NULL,
    consumed_at       TEXT,
    dealer_session_id TEXT,
    created_at        TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pair_sessions_case ON pair_sessions(case_id);

-- Per-device authority to act as a named party. Not an identity claim: it proves
-- only "this browser is the one that created the case" or "this browser redeemed
-- the pairing code". Stored hashed for the same reason as pair codes.
CREATE TABLE IF NOT EXISTS party_sessions (
    id         TEXT PRIMARY KEY,
    case_id    TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    actor      TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_party_sessions_case ON party_sessions(case_id, actor);

-- The idempotency ledger. The UNIQUE constraint is the enforcement mechanism for
-- INV-05, not the application code: a duplicate insert fails at the database even
-- if two requests race past every in-process check.
CREATE TABLE IF NOT EXISTS submission_attempts (
    id                 TEXT    PRIMARY KEY,
    case_id            TEXT    NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    idempotency_key    TEXT    NOT NULL,
    request_hash       TEXT    NOT NULL,
    attempt_number     INTEGER NOT NULL,
    status             TEXT,
    acknowledgement_no TEXT,
    reason_code        TEXT,
    created_at         TEXT    NOT NULL,
    completed_at       TEXT,
    UNIQUE (case_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_submission_attempts_case
    ON submission_attempts(case_id, created_at);

-- Append-only trail with a hash chain. Tamper-evidence aid only: it detects
-- after-the-fact edits to this table. It is not immutability and not a signature
-- (SRS section 3).
CREATE TABLE IF NOT EXISTS audit_events (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id             TEXT    NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    event_type          TEXT    NOT NULL,
    actor               TEXT    NOT NULL,
    state_before        TEXT,
    state_after         TEXT,
    payload_digest      TEXT,
    detail              TEXT,
    created_at          TEXT    NOT NULL,
    previous_event_hash TEXT,
    event_hash          TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_events_case ON audit_events(case_id, id);
