# Submission copy

## Title

Handover29C - a transparent vehicle custody handover prototype

## Summary (188 words)

Handover29C explores a narrow GovTech question: can the transfer of physical
custody of a vehicle to an authorised dealer be prepared as a clear, accessible,
low-latency workflow without inventing a parallel legal process?

The prototype implements a transactional four-state journey - Draft, Initiated,
Dealer Selected, and Custody Transferred - backed by SQLite in WAL mode. It checks
fictional vehicle and dealer fixtures, validates GSTIN structure, rejects skipped
state transitions and invalid odometer readings, records a hash-chained transition
log, and generates a text-extractable Form 29C pre-fill worksheet.

The interface is a focused English/Hindi service flow rather than a dashboard. It
supports keyboard navigation, visible focus, 320px screens, 200% zoom, semantic
status labels, refresh recovery, WebSocket updates, and REST polling fallback.

The boundary is explicit: all people, vehicles, dealers, and registry responses are
fictional. The app does not connect to VAHAN or another government system. Its
worksheet leaves portal declarations, signatures, submission, and acknowledgement
explicitly outstanding; it is not an ownership transfer or claim that legal
liability has changed.

The result is a reproducible implementation and test bed for an evidence-first
transport workflow, with its limitations visible in the product itself.
