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

  it("opens as a focused EPFO transfer journey with no sensitive-data input", () => {
    renderApp();
    expect(
      screen.getByRole("heading", {
        level: 1,
        name: /ravi cannot move his old pf balance/i,
      }),
    ).toBeTruthy();
    expect(screen.getByText(/previous pf account not available to transfer/i)).toBeTruthy();
    expect(screen.getByRole("button", { name: /find what blocks the transfer/i })).toBeTruthy();
    expect(screen.getByText("RAVI KUMAR")).toBeTruthy();
    expect(screen.getByText("RAVI K")).toBeTruthy();
    expect(screen.getAllByText(/date of exit missing/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/no official record is read or changed/i).length).toBeGreaterThan(0);
    expect(screen.queryByRole("combobox")).toBeNull();
  });

  it("completes diagnosis, simulation and official handoff without a modal", async () => {
    mockLiveApi();
    const user = userEvent.setup();
    renderApp();

    await user.click(screen.getByRole("button", { name: /find what blocks the transfer/i }));
    expect(screen.getByRole("heading", { name: /name is not the blocker/i })).toBeTruthy();
    expect(screen.getByText(/date of exit is missing/i)).toBeTruthy();
    expect(screen.queryByRole("dialog")).toBeNull();

    await user.click(screen.getByText(/view technical evidence/i));
    expect(screen.getByText(/EPFO-003 v1.0/)).toBeTruthy();

    await user.click(screen.getByRole("button", { name: /simulate minimum fix/i }));
    expect(await screen.findByRole("heading", { name: /transfer prerequisite is now met/i })).toBeTruthy();
    expect(screen.getByText("2026-05-31")).toBeTruthy();
    expect(screen.getByText(/does not submit or approve a real transfer/i)).toBeTruthy();
    expect(screen.getByText(/no official record was changed/i)).toBeTruthy();
    expect(
      screen.getByRole("link", { name: /open epfo member portal/i }).getAttribute("href"),
    ).toBe(initial.official_handoff.official_url);
    expect(
      screen.getByRole("link", { name: /use official umang epfo services/i }).getAttribute("href"),
    ).toBe("https://web.umang.gov.in/landing/department/epfo.html");
  });

  it("switches the complete core journey and safety copy to Hindi", async () => {
    const user = userEvent.setup();
    renderApp();
    await user.click(screen.getByRole("button", { name: "हिन्दी" }));
    expect(document.documentElement.lang).toBe("hi-IN");
    expect(screen.getByRole("heading", { name: /रवि अपना पुराना PF बैलेंस/i })).toBeTruthy();
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
    await user.click(screen.getByRole("button", { name: /find what blocks the transfer/i }));
    await user.click(screen.getByRole("button", { name: /simulate minimum fix/i }));
    expect(await screen.findByRole("heading", { name: /transfer prerequisite is now met/i })).toBeTruthy();
  });
});
