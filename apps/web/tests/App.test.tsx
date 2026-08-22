import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import staticBundleJson from "../public/identity-rescue-static.json";
import App from "../src/App";
import type { ScenarioAnalysis, SourceReference } from "../src/identityApi";
import { LangProvider } from "../src/i18n/LangProvider";
import { UI, phrase } from "../src/i18n/strings";

const bundle = staticBundleJson as unknown as {
  sources: SourceReference[];
  analyses: Record<string, ScenarioAnalysis>;
};
const initial = bundle.analyses["epfo-preflight|"]!;
const resolved = bundle.analyses["epfo-preflight|ACT-B1"]!;

function json(payload: unknown): Response {
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

function mockLiveApi(): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/sources")) return json(bundle.sources);
      if (url.endsWith("/simulate")) return json(resolved);
      if (url.endsWith("/analyze")) return json(initial);
      throw new Error(`unexpected ${url}`);
    }),
  );
}

function renderApp() {
  return render(
    <LangProvider>
      <App />
    </LangProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  history.replaceState({}, "", "/");
  sessionStorage.clear();
  localStorage.clear();
});

describe("ClaimPath EPFO pre-flight", () => {
  it("has non-empty English and Hindi text for every registered UI key", () => {
    for (const [key, value] of Object.entries(UI)) {
      expect(value.en.trim(), `${key} English`).not.toBe("");
      expect(value.hi.trim(), `${key} Hindi`).not.toBe("");
      expect(phrase(key, "en")).not.toBe(key);
      expect(phrase(key, "hi")).not.toBe(key);
    }
  });

  it("opens as a focused, four-step EPFO journey with safe citizen input", () => {
    renderApp();
    expect(
      screen.getByRole("heading", {
        level: 1,
        name: /ravi’s ₹45,000 pf withdrawal is at risk/i,
      }),
    ).toBeTruthy();
    expect(screen.getByRole("textbox", { name: /what did epfo show you/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /load ravi’s fictional case/i })).toBeTruthy();
    expect(screen.getByText("RAVI KUMAR")).toBeTruthy();
    expect(screen.getByText("RAVI K")).toBeTruthy();
    expect(screen.getAllByText(/date of exit missing/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/no official record is read or changed/i).length).toBeGreaterThan(0);
    expect(screen.queryByRole("combobox")).toBeNull();
  });

  it("rejects identifier-like numbers before any diagnostic request", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    renderApp();
    const note = screen.getByRole("textbox", { name: /what did epfo show you/i });
    await user.clear(note);
    await user.type(note, "My UAN is 123456789012 and the claim failed.");
    await user.click(screen.getByRole("button", { name: /load ravi’s fictional case/i }));
    expect(screen.getByRole("alert").textContent).toMatch(/remove uan/i);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("completes load, diagnose, simulate and official handoff without a modal", async () => {
    mockLiveApi();
    const user = userEvent.setup();
    renderApp();

    await user.click(screen.getByRole("button", { name: /load ravi’s fictional case/i }));
    expect(await screen.findByRole("heading", { name: /three record sources are ready/i })).toBeTruthy();

    await user.click(screen.getByRole("button", { name: /run claim pre-flight/i }));
    expect(screen.getByRole("heading", { name: /name is not the blocker/i })).toBeTruthy();
    expect(screen.getByText(/date of exit is missing/i)).toBeTruthy();
    expect(screen.queryByRole("dialog")).toBeNull();

    await user.click(screen.getByText(/view technical evidence/i));
    expect(screen.getByText(/EPFO-003 v1.0/)).toBeTruthy();

    await user.click(screen.getByRole("button", { name: /simulate minimum fix/i }));
    expect(await screen.findByRole("heading", { name: /modeled blocker is cleared/i })).toBeTruthy();
    expect(screen.getByText("2026-07-31")).toBeTruthy();
    expect(screen.getByText(/not a guarantee of claim approval/i)).toBeTruthy();
    expect(screen.getByText(/no official record was changed/i)).toBeTruthy();
    expect(
      screen.getByRole("link", { name: /open official epfo guidance/i }).getAttribute("href"),
    ).toBe(initial.official_handoff.official_url);
  });

  it("keeps the editable note browser-only and out of API payloads", async () => {
    mockLiveApi();
    const user = userEvent.setup();
    renderApp();
    const note = screen.getByRole("textbox", { name: /what did epfo show you/i });
    await user.clear(note);
    await user.type(note, "The portal did not explain which record stopped the claim.");
    await user.click(screen.getByRole("button", { name: /load ravi’s fictional case/i }));
    expect(sessionStorage.getItem("claimpath.intake.v1")).toContain("did not explain");
    const fetchMock = vi.mocked(fetch);
    const bodies = fetchMock.mock.calls.map((call) => (call[1] as RequestInit | undefined)?.body ?? "");
    expect(bodies.join(" ")).not.toContain("did not explain");
  });

  it("switches the complete core journey and safety copy to Hindi", async () => {
    const user = userEvent.setup();
    renderApp();
    await user.click(screen.getByRole("button", { name: "हिन्दी" }));
    expect(document.documentElement.lang).toBe("hi-IN");
    expect(screen.getByRole("heading", { name: /रवि की ₹45,000 PF निकासी/i })).toBeTruthy();
    expect(screen.getAllByText(/कोई आधिकारिक रिकॉर्ड पढ़ा या बदला नहीं जाता/i).length).toBeGreaterThan(0);
  });

  it("completes from the generated static fallback when the API is unavailable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/v1/identity/")) return new Response("", { status: 404 });
        if (url.endsWith("/identity-rescue-static.json")) return json(staticBundleJson);
        throw new Error(`unexpected ${url}`);
      }),
    );
    const user = userEvent.setup();
    renderApp();
    await user.click(screen.getByRole("button", { name: /load ravi’s fictional case/i }));
    await user.click(await screen.findByRole("button", { name: /run claim pre-flight/i }));
    await user.click(screen.getByRole("button", { name: /simulate minimum fix/i }));
    expect(await screen.findByRole("heading", { name: /modeled blocker is cleared/i })).toBeTruthy();
  });
});
