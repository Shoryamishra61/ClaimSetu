/**
 * One case snapshot, kept current by a WebSocket with a REST poll behind it.
 *
 * The division of authority matters more than the mechanism:
 *
 * -  **The server owns state.** Every snapshot this hook holds was serialised by
 *    the API from the database. The socket carries whole snapshots, never deltas
 *    and never a "you succeeded" signal, so deleting the socket entirely would make
 *    the product slower and not wrong (SRS section 6).
 * -  **The poll is not a degraded mode, it is the floor.** It runs whenever the
 *    socket is not confirmed open, and the interval comes from `/meta` so the
 *    server decides how hard clients hammer it.
 * -  **Snapshots are applied monotonically.** A poll response can land after a
 *    socket push that superseded it; applying it would make the UI walk backwards.
 *    An acknowledged case additionally refuses any non-acknowledged snapshot,
 *    because acknowledgement is terminal on the server, so such a snapshot is
 *    necessarily stale.
 *
 * The transport name is exposed for the source drawer only. Per the UX bar, the
 * main journey never shows connection plumbing: a citizen handing over a car does
 * not need to know what a WebSocket is.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ApiError, getCase } from "../api/client";
import type { CaseSnapshot } from "../api/types";

export type Transport = "connecting" | "socket" | "polling";

export interface CaseStream {
  snapshot: CaseSnapshot | null;
  error: ApiError | null;
  transport: Transport;
  /** Number of snapshots applied. Lets the source drawer show liveness. */
  revision: number;
  /** Force an authoritative read. Used after a mutation and by "check again". */
  refresh: () => Promise<CaseSnapshot | null>;
  /** Apply a snapshot the server just returned from a mutation. */
  apply: (next: CaseSnapshot) => void;
}

/** True when `next` is at least as recent as `current`, and not a stale un-ack. */
export function shouldApply(
  current: CaseSnapshot | null,
  next: CaseSnapshot,
): boolean {
  if (current === null) return true;
  if (current.id !== next.id) return true;
  if (current.is_acknowledged && !next.is_acknowledged) return false;
  // ISO-8601 UTC timestamps compare correctly as strings, which avoids parsing a
  // date just to order two snapshots.
  return next.updated_at >= current.updated_at;
}

function socketUrl(caseId: string): string {
  const scheme = globalThis.location?.protocol === "https:" ? "wss:" : "ws:";
  const host = globalThis.location?.host ?? "";
  return `${scheme}//${host}/ws/cases/${encodeURIComponent(caseId)}`;
}

export function useCaseStream(
  caseId: string | null,
  token: string | null,
  pollIntervalSeconds: number,
): CaseStream {
  const [snapshot, setSnapshot] = useState<CaseSnapshot | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [transport, setTransport] = useState<Transport>("connecting");
  const [revision, setRevision] = useState(0);

  // The latest snapshot as a ref as well as state: `shouldApply` needs it inside
  // callbacks that must not be re-created on every update, or the socket would
  // reconnect on every message.
  const latest = useRef<CaseSnapshot | null>(null);

  const apply = useCallback((next: CaseSnapshot) => {
    if (!shouldApply(latest.current, next)) return;
    latest.current = next;
    setSnapshot(next);
    setRevision((n) => n + 1);
    setError(null);
  }, []);

  const refresh = useCallback(async (): Promise<CaseSnapshot | null> => {
    if (!caseId) return null;
    try {
      const response = await getCase(caseId, token);
      apply(response.case);
      return response.case;
    } catch (caught) {
      if (caught instanceof ApiError) {
        // A poll failure is not worth destroying a good snapshot over: the socket
        // or the next poll may well succeed. A missing case is different -- the
        // case genuinely does not exist, and the user needs to be told.
        if (caught.code === "CASE_NOT_FOUND") setError(caught);
        else if (latest.current === null) setError(caught);
        return null;
      }
      throw caught;
    }
  }, [caseId, token, apply]);

  // Reset when the case changes, so a snapshot from a previous case can never be
  // rendered against a new one.
  useEffect(() => {
    latest.current = null;
    setSnapshot(null);
    setError(null);
    setTransport("connecting");
  }, [caseId]);

  useEffect(() => {
    if (!caseId) return;

    let disposed = false;
    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let attempt = 0;

    // The poll always runs. When the socket is healthy it is a cheap heartbeat that
    // costs one request every few seconds and guarantees the UI cannot sit on a
    // stale snapshot because a push was dropped.
    const pollTimer = setInterval(
      () => {
        void refresh();
      },
      Math.max(1000, pollIntervalSeconds * 1000),
    );

    void refresh();

    const connect = (): void => {
      if (disposed) return;
      let candidate: WebSocket;
      try {
        candidate = new WebSocket(socketUrl(caseId));
      } catch {
        setTransport("polling");
        return;
      }
      socket = candidate;

      candidate.onopen = () => {
        if (disposed) return;
        attempt = 0;
        setTransport("socket");
      };

      candidate.onmessage = (event: MessageEvent<string>) => {
        if (disposed) return;
        try {
          const parsed = JSON.parse(event.data) as {
            type?: string;
            case?: CaseSnapshot;
          };
          // PING carries no state by design; anything unrecognised is ignored
          // rather than guessed at.
          if (parsed.type === "CASE_SNAPSHOT" && parsed.case) apply(parsed.case);
        } catch {
          /* a malformed frame is not a reason to lose a good snapshot */
        }
      };

      candidate.onerror = () => {
        if (!disposed) setTransport("polling");
      };

      candidate.onclose = () => {
        if (disposed) return;
        setTransport("polling");
        socket = null;
        // Capped exponential backoff. The poll is already covering correctness, so
        // there is no need to reconnect aggressively.
        attempt += 1;
        const delay = Math.min(15000, 500 * 2 ** Math.min(attempt, 5));
        reconnectTimer = setTimeout(connect, delay);
      };
    };

    connect();

    return () => {
      disposed = true;
      clearInterval(pollTimer);
      if (reconnectTimer !== null) clearTimeout(reconnectTimer);
      if (socket) {
        socket.onclose = null;
        socket.onerror = null;
        socket.onmessage = null;
        socket.onopen = null;
        try {
          socket.close();
        } catch {
          /* already closing */
        }
      }
    };
  }, [caseId, pollIntervalSeconds, refresh, apply]);

  return useMemo(
    () => ({ snapshot, error, transport, revision, refresh, apply }),
    [snapshot, error, transport, revision, refresh, apply],
  );
}
