import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import type { ScenarioAnalysis, SourceReference } from "../src/identityApi";
import { LangProvider } from "../src/i18n/LangProvider";
import { UI, phrase } from "../src/i18n/strings";

const source: SourceReference = {
  source_id: "SRC-DIGI-001",
  title: "DigiLocker FAQs",
  publisher: "DigiLocker / NeGD",
  url: "https://www.digilocker.gov.in/web/about/faq",
  proposition:
    "DigiLocker says the Aadhaar name should match the DL source name.",
  last_checked_at: "2026-08-22",
};

function analysis(ready = false): ScenarioAnalysis {
  return {
    scenario_id: "digilocker-dl",
    fixture_version: "1.0",
    goal: "DIGILOCKER_FETCH_DL",
    profile: {
      profile_id: "DEMO-ANANYA-01",
      display_name: "Ananya R. Krishnan",
      fictional: true,
      preferred_locale: "en-IN",
      scenario_note: "profile.ananya.note",
    },
    readiness: ready ? "READY_SIMULATION" : "BLOCKED",
    headline_key: ready ? "diagnosis.dl.ready" : "diagnosis.dl.blocked",
    explanation_key: ready
      ? "diagnosis.dl.ready_explanation"
      : "diagnosis.dl.blocked_explanation",
    next_best_action_key: ready
      ? "diagnosis.next.official"
      : "diagnosis.next.compare",
    records: [
      {
        record_id: "REC-AADHAAR-ANANYA",
        authority: "AADHAAR_DEMO",
        label: "Aadhaar demo record",
        fixture_version: "1.0",
        fields: {
          name: {
            original: "ANANYA R KRISHNAN",
            normalized: "ananya r krishnan",
            script: "Latn",
            locale: "en-IN",
            derived_label: "Comparison form",
          },
          dob: {
            original: "1998-02-14",
            normalized: "1998 02 14",
            script: null,
            locale: null,
            derived_label: null,
          },
        },
      },
      {
        record_id: "REC-DL-ANANYA",
        authority: "DL_SOURCE_DEMO",
        label: "Driving Licence source demo record",
        fixture_version: "1.0",
        fields: {
          name: {
            original: ready
              ? "ANANYA RAMESH KRISHNAN"
              : "KRISHNAN ANANYA RAMESH",
            normalized: null,
            script: "Latn",
            locale: "en-IN",
            derived_label: null,
          },
          dob: {
            original: "1998-02-14",
            normalized: null,
            script: null,
            locale: null,
            derived_label: null,
          },
          record_present: {
            original: true,
            normalized: null,
            script: null,
            locale: null,
            derived_label: null,
          },
        },
      },
    ],
    findings: [
      {
        finding_id: "FIND-DL-002",
        rule_id: "DL-002",
        rule_version: "1.0",
        state: ready ? "MATCH_RULE_COMPATIBLE" : "MISMATCH_BLOCKING",
        title_key: ready
          ? "finding.dl.name.pass_title"
          : "finding.dl.name.block_title",
        explanation_key: ready
          ? "finding.dl.name.pass"
          : "finding.dl.name.block",
        causal: !ready,
        evidence_status: "OFFICIAL_SOURCE_INTERPRETED",
        inputs: [
          {
            record_id: "REC-AADHAAR-ANANYA",
            authority: "AADHAAR_DEMO",
            field: "name",
            label: "Aadhaar demo name",
            original_value: "ANANYA R KRISHNAN",
          },
          {
            record_id: "REC-DL-ANANYA",
            authority: "DL_SOURCE_DEMO",
            field: "name",
            label: "Driving Licence source demo name",
            original_value: ready
              ? "ANANYA RAMESH KRISHNAN"
              : "KRISHNAN ANANYA RAMESH",
          },
        ],
        source_ids: ["SRC-DIGI-001"],
        uncertainty_key: "finding.dl.name.uncertainty",
      },
    ],
    dependency_trail_keys: [
      "trail.dl.1",
      "trail.dl.2",
      "trail.dl.3",
      "trail.dl.4",
      "trail.dl.5",
    ],
    actions: [
      {
        action_id: "ACT-A1",
        title_key: "action.a1.title",
        target_record_id: "REC-DL-ANANYA",
        target_field: "name",
        from_value: "KRISHNAN ANANYA RAMESH",
        to_value: "ANANYA RAMESH KRISHNAN",
        effort_key: "effort.issuer",
        effect_key: "action.a1.effect",
        impact_key: "action.a1.impact",
        reversible: true,
        evidence_status: "PROTOTYPE_SIMULATION",
        source_ids: ["SRC-DIGI-001"],
        cost: 45,
      },
      {
        action_id: "ACT-A2",
        title_key: "action.a2.title",
        target_record_id: "REC-AADHAAR-ANANYA",
        target_field: "name",
        from_value: "ANANYA R KRISHNAN",
        to_value: "ANANYA RAMESH KRISHNAN",
        effort_key: "effort.review",
        effect_key: "action.a2.effect",
        impact_key: "action.a2.impact",
        reversible: true,
        evidence_status: "NEEDS_AUTHORITY_VALIDATION",
        source_ids: ["SRC-DIGI-001"],
        cost: 100,
      },
    ],
    recommended_plan: ready
      ? null
      : {
          action_ids: ["ACT-A1"],
          total_cost: 45,
          reason_codes: ["RESOLVES_TARGET", "ONE_STEP"],
          equivalent_plan_count: 1,
        },
    applied_action_ids: ready ? ["ACT-A1"] : [],
    before_after: ready
      ? [
          {
            action_id: "ACT-A1",
            record_label: "Driving Licence source demo record",
            field_label: "name",
            before: "KRISHNAN ANANYA RAMESH",
            after: "ANANYA RAMESH KRISHNAN",
          },
        ]
      : [],
    official_handoff: {
      title_key: "handoff.dl.title",
      step_keys: ["handoff.dl.step1", "handoff.dl.step2", "handoff.dl.step3"],
      official_url: source.url,
      official_label: "DigiLocker official FAQ",
      source_id: source.source_id,
      caveat_key: "handoff.processes_change",
    },
    source_ids: ["SRC-DIGI-001"],
    deterministic: true,
    government_systems_contacted: 0,
  };
}

function json(payload: unknown): Response {
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
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

describe("Identity Rescue Scenario A", () => {
  it("has non-empty English and Hindi text for every registered UI key", () => {
    for (const [key, value] of Object.entries(UI)) {
      expect(value.en.trim(), `${key} English`).not.toBe("");
      expect(value.hi.trim(), `${key} Hindi`).not.toBe("");
      expect(phrase(key, "en")).not.toBe(key);
      expect(phrase(key, "hi")).not.toBe(key);
    }
  });

  it("opens goal-first with exactly three fictional citizen problems", () => {
    renderApp();
    expect(
      screen.getByRole("heading", { level: 1, name: /when records disagree/i }),
    ).toBeTruthy();
    expect(screen.getAllByText("FICTIONAL CASE")).toHaveLength(3);
    expect(
      screen.getAllByRole("button", { name: /try this case/i }),
    ).toHaveLength(3);
    expect(screen.queryByText(/vehicle handover/i)).toBeNull();
  });

  it("switches the full shell and safety copy to Hindi", async () => {
    const user = userEvent.setup();
    renderApp();
    await user.click(screen.getByRole("button", { name: "हिन्दी" }));
    expect(document.documentElement.lang).toBe("hi-IN");
    expect(
      screen.getByRole("heading", { level: 1, name: /जब रिकॉर्ड अलग हों/i }),
    ).toBeTruthy();
    expect(screen.getByText(/असली Aadhaar, PAN, UAN, OTP/i)).toBeTruthy();
  });

  it("shows causal evidence, simulates the recommended route, and reaches official handoff", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/sources")) return json([source]);
        if (url.endsWith("/simulate")) return json(analysis(true));
        if (url.endsWith("/analyze")) return json(analysis(false));
        throw new Error(`unexpected ${url}`);
      }),
    );
    const user = userEvent.setup();
    renderApp();
    await user.click(
      screen.getAllByRole("button", { name: /try this case/i })[0]!,
    );
    expect(
      await screen.findByRole("heading", {
        name: /blocked by one record mismatch/i,
      }),
    ).toBeTruthy();
    expect(screen.getAllByText("ANANYA R KRISHNAN").length).toBeGreaterThan(0);
    expect(
      screen.getAllByText("KRISHNAN ANANYA RAMESH").length,
    ).toBeGreaterThan(0);
    await user.click(screen.getByText("Show the evidence"));
    expect(screen.getByText(/DL-002 v1.0/)).toBeTruthy();
    expect(
      screen
        .getByRole("link", { name: /DigiLocker FAQs/i })
        .getAttribute("href"),
    ).toBe(source.url);

    await user.click(screen.getByRole("button", { name: /compare ways/i }));
    const recommended = screen
      .getByText("Recommended in this simulation")
      .closest("article")!;
    await user.click(
      within(recommended).getByRole("button", { name: /simulate this route/i }),
    );
    const dialog = screen.getByRole("dialog", {
      name: /simulate this correction/i,
    });
    expect(
      within(dialog).getByText(/No government record will be contacted/i),
    ).toBeTruthy();
    await user.click(
      within(dialog).getByRole("button", { name: /simulate correction/i }),
    );

    expect(
      (await screen.findAllByText("Ready in this simulation")).length,
    ).toBeGreaterThan(0);
    expect(screen.getByText("No official record was changed")).toBeTruthy();
    expect(screen.getByText("KRISHNAN ANANYA RAMESH")).toBeTruthy();
    expect(screen.getByText("ANANYA RAMESH KRISHNAN")).toBeTruthy();
    expect(
      screen
        .getByRole("link", { name: /open official source/i })
        .getAttribute("href"),
    ).toBe(source.url);
  });

  it("completes the same deterministic journey from the generated static fallback", async () => {
    const bundle = {
      fixture_version: "1.0",
      generated_from: "IdentityRescueEngine",
      deterministic: true,
      government_systems_contacted: 0,
      sources: [source],
      analyses: {
        "digilocker-dl|": analysis(false),
        "digilocker-dl|ACT-A1": analysis(true),
      },
    };
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/v1/identity/")) {
          return new Response("", { status: 404 });
        }
        if (url.endsWith("/identity-rescue-static.json")) return json(bundle);
        throw new Error(`unexpected ${url}`);
      }),
    );
    const user = userEvent.setup();
    renderApp();
    await user.click(
      screen.getAllByRole("button", { name: /try this case/i })[0]!,
    );
    expect(
      await screen.findByRole("heading", {
        name: /blocked by one record mismatch/i,
      }),
    ).toBeTruthy();
    await user.click(screen.getByRole("button", { name: /compare ways/i }));
    const recommended = screen
      .getByText("Recommended in this simulation")
      .closest("article")!;
    await user.click(
      within(recommended).getByRole("button", { name: /simulate this route/i }),
    );
    await user.click(
      screen.getByRole("button", { name: /simulate correction/i }),
    );
    expect(
      (await screen.findAllByText("Ready in this simulation")).length,
    ).toBeGreaterThan(0);
  });
});
