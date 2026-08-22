import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
  type ReactNode,
} from "react";
import {
  ArrowLeft,
  ArrowRight,
  BookOpenText,
  CarProfile,
  Check,
  CheckCircle,
  DeviceMobile,
  Flag,
  IdentificationCard,
  Info,
  MapTrifold,
  Question,
  ShieldCheck,
  SlidersHorizontal,
  WarningCircle,
} from "@phosphor-icons/react";

import {
  analyzeScenario,
  getSources,
  simulateScenario,
  type CorrectionAction,
  type Finding,
  type ScenarioAnalysis,
  type SourceReference,
  type SyntheticRecord,
} from "./identityApi";
import { useLang } from "./i18n/LangProvider";

const CASE_KEY = "identity-rescue.case.v1";
const INTAKE_KEY = "identity-rescue.intake.v1";
const BASE_PATH =
  import.meta.env.BASE_URL === "/"
    ? ""
    : import.meta.env.BASE_URL.replace(/\/$/, "");
type Stage = "diagnosis" | "options" | "result";
interface IntakeContext {
  scenarioId: string;
  failure: string;
  description: string;
}
type Route =
  | { kind: "home" }
  | { kind: "case"; scenarioId: string }
  | { kind: "sources" }
  | { kind: "privacy" };

const scenarioCards = [
  {
    id: "digilocker-dl",
    title: "scenario.dl.title",
    body: "scenario.dl.body",
    enabled: true,
  },
  {
    id: "epfo-preflight",
    title: "scenario.epfo.title",
    body: "scenario.epfo.body",
    enabled: true,
  },
  {
    id: "life-event",
    title: "scenario.life.title",
    body: "scenario.life.body",
    enabled: true,
  },
] as const;

const scenarioIntake = {
  "digilocker-dl": {
    profile: "Ananya R. Krishnan — DEMO-ANANYA-01",
    description: "DigiLocker could not fetch the Driving Licence after the details check.",
    records: ["intake.record.aadhaar", "intake.record.dl"],
    route: ["intake.route.identity", "intake.route.transport", "intake.route.digilocker"],
  },
  "epfo-preflight": {
    profile: "Arvind N. Rao — DEMO-ARVIND-02",
    description: "The fictional PF/KYC pre-flight still fails after checking the displayed name.",
    records: ["intake.record.aadhaar", "intake.record.epfo", "intake.record.pan"],
    route: ["intake.route.identity", "intake.route.epfo", "intake.route.pfGoal"],
  },
  "life-event": {
    profile: "Meera Nair — DEMO-MEERA-03",
    description: "The fictional records show different names after a life event.",
    records: ["intake.record.aadhaar", "intake.record.dl", "intake.record.pan"],
    route: ["intake.route.chosenName", "intake.route.transport", "intake.route.reconcile"],
  },
} as const;

function routeFromPath(pathname: string): Route {
  const appPath =
    BASE_PATH && pathname.startsWith(BASE_PATH)
      ? pathname.slice(BASE_PATH.length) || "/"
      : pathname;
  if (appPath === "/sources") return { kind: "sources" };
  if (appPath === "/privacy") return { kind: "privacy" };
  const match = /^\/case\/([^/]+)$/.exec(appPath);
  return match
    ? { kind: "case", scenarioId: decodeURIComponent(match[1]!) }
    : { kind: "home" };
}

function navigate(path: string): void {
  history.pushState({}, "", `${BASE_PATH}${path}` || "/");
  globalThis.dispatchEvent(new PopStateEvent("popstate"));
}

function readSession(scenarioId: string): string[] {
  try {
    const parsed = JSON.parse(sessionStorage.getItem(CASE_KEY) ?? "null") as {
      scenarioId?: string;
      applied?: string[];
    } | null;
    return parsed?.scenarioId === scenarioId && Array.isArray(parsed.applied)
      ? parsed.applied
      : [];
  } catch {
    return [];
  }
}

function saveSession(scenarioId: string, applied: string[]): void {
  try {
    sessionStorage.setItem(CASE_KEY, JSON.stringify({ scenarioId, applied }));
  } catch {
    /* session persistence is optional */
  }
}

function readIntake(scenarioId: string): IntakeContext | null {
  try {
    const parsed = JSON.parse(sessionStorage.getItem(INTAKE_KEY) ?? "null") as
      | IntakeContext
      | null;
    return parsed?.scenarioId === scenarioId ? parsed : null;
  } catch {
    return null;
  }
}

function saveIntake(intake: IntakeContext): void {
  try {
    sessionStorage.setItem(INTAKE_KEY, JSON.stringify(intake));
  } catch {
    /* intake context is optional and remains browser-only */
  }
}

function clearSession(): void {
  try {
    sessionStorage.removeItem(CASE_KEY);
    sessionStorage.removeItem(INTAKE_KEY);
  } catch {
    /* already clear enough */
  }
}

function valueText(
  value: string | boolean | null,
  yes: string,
  no: string,
): string {
  if (typeof value === "boolean") return value ? yes : no;
  return value ?? "—";
}

function Shell({
  children,
  onHome,
}: {
  children: ReactNode;
  onHome: () => void;
}) {
  const { lang, setLang, t } = useLang();
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        {t("a11y.skip")}
      </a>
      <div className="trust-strip" role="note">
        <Info aria-hidden="true" weight="bold" />
        {t("disclosure.global")}
      </div>
      <header className="site-header">
        <div className="header-inner">
          <button
            className="brand"
            type="button"
            onClick={onHome}
            aria-label={`${t("app.name")}: ${t("nav.home")}`}
          >
            <span className="brand-mark" aria-hidden="true">
              IR
            </span>
            <span>
              <strong>{t("app.name")}</strong>
              <small>{t("app.tagline")}</small>
            </span>
          </button>
          <nav className="header-actions" aria-label="Primary">
            <button
              className="text-button"
              type="button"
              onClick={() => navigate("/sources")}
            >
              <BookOpenText aria-hidden="true" />
              {t("nav.sourcesShort")}
            </button>
            <div className="language-switch" aria-label={t("nav.language")}>
              <button
                type="button"
                aria-pressed={lang === "en"}
                onClick={() => setLang("en")}
              >
                {t("nav.english")}
              </button>
              <button
                type="button"
                aria-pressed={lang === "hi"}
                onClick={() => setLang("hi")}
              >
                {t("nav.hindi")}
              </button>
            </div>
          </nav>
        </div>
      </header>
      {children}
      <footer>
        <div>
          <button type="button" onClick={() => navigate("/sources")}>
            {t("nav.sources")}
          </button>
          <button type="button" onClick={() => navigate("/privacy")}>
            {t("nav.privacy")}
          </button>
          <button type="button" onClick={onHome}>
            {t("common.reset")}
          </button>
        </div>
        <p>{t("disclosure.global")}</p>
      </footer>
    </div>
  );
}

function Home({ onStart }: { onStart: (id: string) => void }) {
  const { t } = useLang();
  const [scenarioId, setScenarioId] = useState<keyof typeof scenarioIntake>(
    "digilocker-dl",
  );
  const [failure, setFailure] = useState("details-mismatch");
  const [description, setDescription] = useState<string>(
    scenarioIntake["digilocker-dl"].description,
  );
  const [error, setError] = useState("");
  const selected = scenarioIntake[scenarioId];
  const selectedCard = scenarioCards.find((card) => card.id === scenarioId)!;
  const updateScenario = (value: string) => {
    const nextId = value as keyof typeof scenarioIntake;
    setScenarioId(nextId);
    setDescription(scenarioIntake[nextId].description);
    setError("");
  };
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = description.trim();
    if (trimmed.length < 10) {
      setError(t("intake.error.short"));
      return;
    }
    if (/\b\d{6,}\b/.test(trimmed)) {
      setError(t("intake.error.sensitive"));
      return;
    }
    saveIntake({ scenarioId, failure, description: trimmed });
    onStart(scenarioId);
  };
  return (
    <main id="main" className="intake-page" tabIndex={-1}>
      <section className="intake-hero">
        <h1>{t("home.title")}</h1>
        <p className="hero-copy">{t("home.body")}</p>
      </section>
      <Progress current={0} />
      <div className="intake-layout">
        <form className="intake-form" onSubmit={submit} noValidate>
          <div className="field-group">
            <label htmlFor="service-goal">{t("intake.goal")}</label>
            <select
              id="service-goal"
              value={scenarioId}
              onChange={(event) => updateScenario(event.target.value)}
            >
              {scenarioCards.map((card) => (
                <option key={card.id} value={card.id}>
                  {t(card.title)}
                </option>
              ))}
            </select>
          </div>
          <div className="field-group">
            <label htmlFor="failure-message">{t("intake.failure")}</label>
            <select
              id="failure-message"
              value={failure}
              onChange={(event) => setFailure(event.target.value)}
            >
              <option value="details-mismatch">{t("intake.failure.mismatch")}</option>
              <option value="record-not-found">{t("intake.failure.notFound")}</option>
              <option value="other">{t("intake.failure.other")}</option>
            </select>
          </div>
          <div className="field-group">
            <label htmlFor="problem-description">{t("intake.describe")}</label>
            <textarea
              id="problem-description"
              maxLength={280}
              value={description}
              onChange={(event) => {
                setDescription(event.target.value);
                setError("");
              }}
              aria-describedby="description-help description-count"
              aria-invalid={Boolean(error)}
            />
            <div className="field-help-row">
              <span id="description-help">{t("intake.describeHelp")}</span>
              <span id="description-count">{description.length}/280</span>
            </div>
            {error && <p className="field-error" role="alert">{error}</p>}
          </div>
          <div className="field-group">
            <label htmlFor="fictional-profile">{t("intake.profile")}</label>
            <select
              id="fictional-profile"
              value={scenarioId}
              onChange={(event) => updateScenario(event.target.value)}
            >
              {Object.entries(scenarioIntake).map(([id, config]) => (
                <option key={id} value={id}>{config.profile}</option>
              ))}
            </select>
          </div>
          <details className="intake-records">
            <summary>{t("intake.records")}</summary>
            <ul>
              {selected.records.map((key) => (
                <li key={key}>
                  <IdentificationCard aria-hidden="true" />
                  <span>{t(key)}</span>
                  <strong>{t("intake.included")}</strong>
                </li>
              ))}
            </ul>
          </details>
          <div className="intake-submit-row">
            <button className="primary intake-submit" type="submit">
              <ShieldCheck aria-hidden="true" weight="bold" />
              {t("intake.submit")}
              <ArrowRight aria-hidden="true" weight="bold" />
            </button>
            <span>{t("intake.next")}</span>
          </div>
        </form>
        <aside className="route-preview" aria-labelledby="route-preview-title">
          <h2 id="route-preview-title">{t("intake.routeTitle")}</h2>
          <ol className="route-nodes">
            {selected.route.map((key, index) => {
              const Icon = index === 0 ? IdentificationCard : index === 1 ? CarProfile : DeviceMobile;
              return (
                <li className={index === 1 ? "possible-blocker" : ""} key={key}>
                  <span className="route-number">{index + 1}</span>
                  <Icon aria-hidden="true" weight="duotone" />
                  <strong>{t(key)}</strong>
                  <small>{index === 1 ? t("intake.possible") : index === 2 ? t("intake.goalNode") : t("intake.included")}</small>
                  {index < selected.route.length - 1 && <ArrowRight className="route-arrow" aria-hidden="true" />}
                </li>
              );
            })}
          </ol>
          <div className="result-preview-list">
            <h3>{t("intake.resultTitle")}</h3>
            <p><WarningCircle aria-hidden="true" /> <span><strong>{t("intake.result.blocker")}</strong>{t("intake.result.blockerBody")}</span></p>
            <p><Question aria-hidden="true" /> <span><strong>{t("intake.result.why")}</strong>{t("intake.result.whyBody")}</span></p>
            <p><SlidersHorizontal aria-hidden="true" /> <span><strong>{t("intake.result.routes")}</strong>{t("intake.result.routesBody")}</span></p>
            <p><Flag aria-hidden="true" /> <span><strong>{t("intake.result.destination")}</strong>{t("intake.result.destinationBody")}</span></p>
          </div>
          <p className="selected-goal"><MapTrifold aria-hidden="true" /> {t(selectedCard.title)}</p>
        </aside>
      </div>
      <p className="intake-safety"><WarningCircle aria-hidden="true" weight="bold" /> {t("disclosure.sensitiveExtended")}</p>
    </main>
  );
}

function Progress({ stage, current }: { stage?: Stage; current?: number }) {
  const { t } = useLang();
  const labels = [
    "progress.start",
    "progress.diagnose",
    "progress.compare",
    "progress.next",
  ];
  const active = current ?? (stage === "diagnosis" ? 1 : stage === "options" ? 2 : 3);
  return (
    <nav className="case-progress" aria-label={t("case.progress")}>
      <ol>
        {labels.map((key, index) => (
          <li
            className={
              index < active ? "done" : index === active ? "active" : "future"
            }
            key={key}
          >
            <span aria-hidden="true">{index < active ? <Check weight="bold" /> : index + 1}</span>
            <span><strong>{t(key)}</strong><small>{t(`${key}.help`)}</small></span>
          </li>
        ))}
      </ol>
    </nav>
  );
}

function Status({ analysis }: { analysis: ScenarioAnalysis }) {
  const { t } = useLang();
  const ready = analysis.readiness === "READY_SIMULATION";
  return (
    <section
      className={`readiness ${ready ? "ready" : "blocked"}`}
      aria-labelledby="result-heading"
    >
      <p className="eyebrow">{t("status.result")}</p>
      <div className="status-label">
        <span aria-hidden="true">
          {ready ? <CheckCircle weight="fill" /> : <WarningCircle weight="fill" />}
        </span>
        {t(`status.${analysis.readiness}`)}
      </div>
      <h2 id="result-heading">{t(analysis.headline_key)}</h2>
      <p>{t(analysis.explanation_key)}</p>
      <p className="next-best">
        <strong>{t(analysis.next_best_action_key)}</strong>
      </p>
    </section>
  );
}

function RecordCard({ record }: { record: SyntheticRecord }) {
  const { t } = useLang();
  return (
    <article className="record-card">
      <div className="record-heading">
        <h3>{record.label}</h3>
        <span className="demo-badge">{t("record.fictional")}</span>
      </div>
      <dl>
        {Object.entries(record.fields).map(([name, field]) => (
          <div key={name}>
            <dt>{t(`field.${name}`)}</dt>
            <dd>
              {valueText(field.original, t("common.yes"), t("common.no"))}
            </dd>
          </div>
        ))}
      </dl>
    </article>
  );
}

function FindingCard({
  finding,
  sources,
}: {
  finding: Finding;
  sources: SourceReference[];
}) {
  const { t } = useLang();
  const matchedSources = sources.filter((source) =>
    finding.source_ids.includes(source.source_id),
  );
  return (
    <article className={`finding ${finding.causal ? "causal" : "supporting"}`}>
      <div className="finding-heading">
        <span className="finding-icon" aria-hidden="true">
          {finding.causal ? <WarningCircle weight="fill" /> : <CheckCircle weight="fill" />}
        </span>
        <div>
          <p className="finding-state">{t(`finding.${finding.state}`)}</p>
          <h3>{t(finding.title_key)}</h3>
        </div>
      </div>
      <p>{t(finding.explanation_key)}</p>
      {finding.causal && (
        <details>
          <summary>{t("diagnosis.evidence")}</summary>
          <div className="evidence-body">
            <h4>{t("evidence.rule")}</h4>
            <p>
              <strong>{t("evidence.ruleId")}:</strong> {finding.rule_id} v
              {finding.rule_version}
            </p>
            <h4>{t("evidence.inputs")}</h4>
            <dl>
              {finding.inputs.map((input) => (
                <div key={`${input.record_id}-${input.field}`}>
                  <dt>{input.label}</dt>
                  <dd>
                    {valueText(
                      input.original_value,
                      t("common.yes"),
                      t("common.no"),
                    )}
                  </dd>
                </div>
              ))}
            </dl>
            <h4>{t("evidence.source")}</h4>
            {matchedSources.map((source) => (
              <p key={source.source_id}>
                <a href={source.url} target="_blank" rel="noopener noreferrer">
                  {source.title} — {source.publisher}
                </a>
              </p>
            ))}
            {finding.uncertainty_key && (
              <>
                <h4>{t("evidence.limit")}</h4>
                <p>{t(finding.uncertainty_key)}</p>
              </>
            )}
          </div>
        </details>
      )}
    </article>
  );
}

function SimulationDialog({
  action,
  onCancel,
  onConfirm,
  busy,
}: {
  action: CorrectionAction;
  onCancel: () => void;
  onConfirm: () => void;
  busy: boolean;
}) {
  const { t } = useLang();
  const dialog = useRef<HTMLDivElement>(null);
  useEffect(() => {
    dialog.current?.querySelector<HTMLButtonElement>("button")?.focus();
  }, []);
  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      event.preventDefault();
      onCancel();
    }
    if (event.key !== "Tab" || !dialog.current) return;
    const controls = Array.from(
      dialog.current.querySelectorAll<HTMLButtonElement>(
        "button:not([disabled])",
      ),
    );
    if (!controls.length) return;
    const first = controls[0]!;
    const last = controls[controls.length - 1]!;
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };
  return (
    <div
      className="modal-backdrop"
      onMouseDown={(event) => {
        if (event.currentTarget === event.target) onCancel();
      }}
    >
      <div
        ref={dialog}
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="simulation-title"
        onKeyDown={onKeyDown}
      >
        <p className="eyebrow">{t("scenario.fictional")}</p>
        <h2 id="simulation-title">{t("dialog.title")}</h2>
        <p>{t("dialog.body")}</p>
        <div className="selected-change">
          <strong>{t(action.title_key)}</strong>
          <span>
            {String(action.from_value)} → {String(action.to_value)}
          </span>
        </div>
        <div className="modal-actions">
          <button className="secondary" type="button" onClick={onCancel}>
            {t("dialog.cancel")}
          </button>
          <button
            className="primary"
            type="button"
            disabled={busy}
            onClick={onConfirm}
          >
            {busy ? t("common.loading") : t("dialog.confirm")}
          </button>
        </div>
      </div>
    </div>
  );
}

function Options({
  analysis,
  onBack,
  onSelect,
}: {
  analysis: ScenarioAnalysis;
  onBack: () => void;
  onSelect: (action: CorrectionAction, trigger: HTMLButtonElement) => void;
}) {
  const { t } = useLang();
  const recommended = new Set(analysis.recommended_plan?.action_ids ?? []);
  return (
    <section className="flow-section">
      <button className="back-button" type="button" onClick={onBack}>
        <ArrowLeft aria-hidden="true" /> {t("common.back")}
      </button>
      <h2>{t("options.title")}</h2>
      <p className="section-intro">{t("options.body")}</p>
      <div className="option-grid">
        {analysis.actions.map((action) => {
          const isRecommended = recommended.has(action.action_id);
          return (
            <article
              className={`option-card ${isRecommended ? "recommended" : ""}`}
              key={action.action_id}
            >
              <p className="option-label">
                {isRecommended
                  ? t("options.recommended")
                  : t("options.alternative")}
              </p>
              <h3>{t(action.title_key)}</h3>
              <dl>
                <div>
                  <dt>{t("options.change")}</dt>
                  <dd>
                    <span className="mono">{String(action.from_value)}</span>
                    <span aria-hidden="true"> → </span>
                    <span className="mono">{String(action.to_value)}</span>
                  </dd>
                </div>
                <div>
                  <dt>{t("options.effect")}</dt>
                  <dd>{t(action.effect_key)}</dd>
                </div>
                <div>
                  <dt>{t("options.impact")}</dt>
                  <dd>{t(action.impact_key)}</dd>
                </div>
                <div>
                  <dt>{t("options.effort")}</dt>
                  <dd>{t(action.effort_key)}</dd>
                </div>
                <div>
                  <dt>{t("options.cost")}</dt>
                  <dd>{action.cost}</dd>
                </div>
              </dl>
              <button
                className={isRecommended ? "primary" : "secondary"}
                type="button"
                onClick={(event) => onSelect(action, event.currentTarget)}
              >
                {t("options.simulate")}
              </button>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function Result({
  analysis,
  onUndo,
}: {
  analysis: ScenarioAnalysis;
  onUndo: () => void;
}) {
  const { t } = useLang();
  const remaining = analysis.findings.filter(
    (finding) => finding.state === "VARIANT_NON_BLOCKING",
  );
  return (
    <section className="flow-section">
      <h2>{t("result.title")}</h2>
      <div className="no-real-change">
        <CheckCircle aria-hidden="true" weight="fill" />
        <strong>{t("result.noRealChange")}</strong>
      </div>
      {analysis.before_after.length > 0 && (
        <section className="before-after" aria-labelledby="changed-heading">
          <h3 id="changed-heading">{t("result.changed")}</h3>
          {analysis.before_after.map((change) => (
            <dl key={change.action_id}>
              <div>
                <dt>{t("result.before")}</dt>
                <dd>{String(change.before)}</dd>
              </div>
              <div>
                <dt>{t("result.after")}</dt>
                <dd>{String(change.after)}</dd>
              </div>
            </dl>
          ))}
        </section>
      )}
      {remaining.length > 0 && (
        <section className="remaining-findings">
          <h3>{t("result.remaining")}</h3>
          <ul>
            {remaining.map((finding) => (
              <li key={finding.finding_id}>
                <strong>{t(finding.title_key)}</strong>
                <span>{t(finding.explanation_key)}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
      <section className="handoff">
        <h2>{t(analysis.official_handoff.title_key)}</h2>
        <ol>
          {analysis.official_handoff.step_keys.map((key) => (
            <li key={key}>{t(key)}</li>
          ))}
        </ol>
        <p className="caveat">{t(analysis.official_handoff.caveat_key)}</p>
        <div className="result-actions">
          <a
            className="primary button-link"
            href={analysis.official_handoff.official_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            {t("handoff.open")} ↗
          </a>
          <button className="secondary" type="button" onClick={onUndo}>
            {t("result.undo")}
          </button>
        </div>
      </section>
    </section>
  );
}

function CasePage({
  scenarioId,
  onReset,
}: {
  scenarioId: string;
  onReset: () => void;
}) {
  const { t } = useLang();
  const intake = useMemo(() => readIntake(scenarioId), [scenarioId]);
  const [analysis, setAnalysis] = useState<ScenarioAnalysis | null>(null);
  const [sources, setSources] = useState<SourceReference[]>([]);
  const [stage, setStage] = useState<Stage>("diagnosis");
  const [selectedAction, setSelectedAction] = useState<CorrectionAction | null>(
    null,
  );
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState(false);
  const liveRegion = useRef<HTMLDivElement>(null);
  const simulationTrigger = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    let current = true;
    setBusy(true);
    setError(false);
    const applied = readSession(scenarioId);
    Promise.all([analyzeScenario(scenarioId, applied), getSources()])
      .then(([next, sourceList]) => {
        if (!current) return;
        setAnalysis(next);
        setSources(sourceList);
        setStage(
          next.readiness === "READY_SIMULATION" ? "result" : "diagnosis",
        );
      })
      .catch(() => {
        if (current) setError(true);
      })
      .finally(() => {
        if (current) setBusy(false);
      });
    return () => {
      current = false;
    };
  }, [scenarioId]);

  const confirmSimulation = async () => {
    if (!analysis || !selectedAction) return;
    setBusy(true);
    setError(false);
    try {
      const next = await simulateScenario(
        scenarioId,
        selectedAction.action_id,
        analysis.applied_action_ids,
      );
      setAnalysis(next);
      saveSession(scenarioId, next.applied_action_ids);
      setStage(next.readiness === "READY_SIMULATION" ? "result" : "diagnosis");
      setSelectedAction(null);
      requestAnimationFrame(() => liveRegion.current?.focus());
    } catch {
      setError(true);
      setSelectedAction(null);
    } finally {
      setBusy(false);
    }
  };
  const undo = async () => {
    if (!analysis) return;
    const applied = analysis.applied_action_ids.slice(0, -1);
    setBusy(true);
    try {
      const next = await analyzeScenario(scenarioId, applied);
      setAnalysis(next);
      saveSession(scenarioId, applied);
      setStage("diagnosis");
    } finally {
      setBusy(false);
    }
  };

  const closeSimulation = () => {
    setSelectedAction(null);
    requestAnimationFrame(() => simulationTrigger.current?.focus());
  };

  const prefix =
    scenarioId === "epfo-preflight"
      ? "epfo"
      : scenarioId === "life-event"
        ? "life"
        : "dl";
  const titleKey = `scenario.${prefix}.title`;
  if (busy && !analysis)
    return (
      <main id="main" className="page" tabIndex={-1}>
        <h1>{t(titleKey)}</h1>
        <p role="status">{t("common.loading")}</p>
      </main>
    );
  if (error || !analysis)
    return (
      <main id="main" className="page" tabIndex={-1}>
        <h1>{t(titleKey)}</h1>
        <p role="alert">{t("common.error")}</p>
        <button className="primary" type="button" onClick={onReset}>
          {t("common.reset")}
        </button>
      </main>
    );
  const primaryIds =
    prefix === "life"
      ? new Set(["REC-AADHAAR-MEERA", "REC-DL-MEERA"])
      : prefix === "dl"
        ? new Set(["REC-AADHAAR-ANANYA", "REC-DL-ANANYA"])
        : new Set(analysis.records.map((record) => record.record_id));
  const primaryRecords = analysis.records.filter((record) =>
    primaryIds.has(record.record_id),
  );
  const otherRecords = analysis.records.filter(
    (record) => !primaryIds.has(record.record_id),
  );
  const visibleFindings =
    prefix === "dl"
      ? analysis.findings.filter((finding) => finding.causal)
      : analysis.findings.filter(
          (finding) =>
            finding.causal || finding.state === "VARIANT_NON_BLOCKING",
        );
  return (
    <main id="main" className="page case-page" tabIndex={-1}>
      <button className="back-button" type="button" onClick={onReset}>
        <ArrowLeft aria-hidden="true" /> {t("nav.home")}
      </button>
      <header className="case-header">
        <div>
          <p className="eyebrow">{t("case.demoData")}</p>
          <h1>{t(titleKey)}</h1>
          <p>{t(`case.goal.${prefix}`)}</p>
        </div>
        <div className="profile-chip">
          <span>{t("case.profile")}</span>
          <strong>{analysis.profile.display_name}</strong>
          <small>{analysis.profile.profile_id}</small>
        </div>
      </header>
      <p className="privacy-line">
        <Info aria-hidden="true" weight="bold" />
        {t("disclosure.sensitive")}
      </p>
      {intake && (
        <section className="intake-context" aria-labelledby="intake-context-title">
          <div>
            <p className="eyebrow">{t("intake.contextLabel")}</p>
            <h2 id="intake-context-title">{t("intake.contextTitle")}</h2>
          </div>
          <p>{intake.description}</p>
          <small>{t("intake.contextLimit")}</small>
        </section>
      )}
      <Progress stage={stage} />
      <div
        ref={liveRegion}
        className="sr-only"
        role="status"
        aria-live="polite"
        tabIndex={-1}
      >
        {t(`status.${analysis.readiness}`)}
      </div>
      <Status analysis={analysis} />
      {stage === "diagnosis" && (
        <>
          <section className="flow-section">
            <h2>{t("diagnosis.records")}</h2>
            <div className="record-grid">
              {primaryRecords.map((record) => (
                <RecordCard key={record.record_id} record={record} />
              ))}
            </div>
            {otherRecords.length > 0 && (
              <details className="other-records">
                <summary>{t("records.other")}</summary>
                <div className="record-grid">
                  {otherRecords.map((record) => (
                    <RecordCard key={record.record_id} record={record} />
                  ))}
                </div>
              </details>
            )}
          </section>
          <section className="flow-section finding-stack">
            {visibleFindings.map((finding) => (
              <FindingCard
                key={finding.finding_id}
                finding={finding}
                sources={sources}
              />
            ))}
          </section>
          <section className="flow-section dependency">
            <h2>{t("diagnosis.trail")}</h2>
            <ol>
              {analysis.dependency_trail_keys.map((key) => (
                <li key={key}>{t(key)}</li>
              ))}
            </ol>
          </section>
          <div className="sticky-action">
            <button
              className="primary"
              type="button"
              onClick={() => setStage("options")}
            >
              {t("diagnosis.compare")}
            </button>
          </div>
        </>
      )}
      {stage === "options" && (
        <Options
          analysis={analysis}
          onBack={() => setStage("diagnosis")}
          onSelect={(action, trigger) => {
            simulationTrigger.current = trigger;
            setSelectedAction(action);
          }}
        />
      )}
      {stage === "result" && (
        <Result analysis={analysis} onUndo={() => void undo()} />
      )}
      {selectedAction && (
        <SimulationDialog
          action={selectedAction}
          busy={busy}
          onCancel={closeSimulation}
          onConfirm={() => void confirmSimulation()}
        />
      )}
    </main>
  );
}

function SourcesPage() {
  const { t } = useLang();
  const [sources, setSources] = useState<SourceReference[]>([]);
  useEffect(() => {
    void getSources().then(setSources);
  }, []);
  return (
    <main id="main" className="page text-page" tabIndex={-1}>
      <h1>{t("sources.title")}</h1>
      <p>{t("sources.body")}</p>
      {sources.map((source) => (
        <article className="source-card" key={source.source_id}>
          <p className="source-id">{source.source_id}</p>
          <h2>{source.title}</h2>
          <p>{source.publisher}</p>
          <dl>
            <div>
              <dt>{t("sources.proposition")}</dt>
              <dd>{source.proposition}</dd>
            </div>
            <div>
              <dt>{t("sources.checked")}</dt>
              <dd>{source.last_checked_at}</dd>
            </div>
          </dl>
          <a href={source.url} target="_blank" rel="noopener noreferrer">
            {t("sources.external")} ↗
          </a>
        </article>
      ))}
    </main>
  );
}

function PrivacyPage() {
  const { t } = useLang();
  return (
    <main id="main" className="page text-page" tabIndex={-1}>
      <h1>{t("privacy.title")}</h1>
      <p>{t("privacy.body")}</p>
      <p>{t("privacy.ai")}</p>
      <div className="privacy-principles">
        <strong>{t("disclosure.global")}</strong>
        <p>{t("disclosure.sensitive")}</p>
      </div>
    </main>
  );
}

export default function App() {
  const { t } = useLang();
  const [route, setRoute] = useState<Route>(() =>
    routeFromPath(location.pathname),
  );
  useEffect(() => {
    const update = () => setRoute(routeFromPath(location.pathname));
    addEventListener("popstate", update);
    return () => removeEventListener("popstate", update);
  }, []);
  const reset = () => {
    clearSession();
    navigate("/");
  };
  const title = useMemo(
    () => {
      if (route.kind === "home") return t("home.title");
      if (route.kind === "sources") return t("sources.title");
      if (route.kind === "privacy") return t("privacy.title");
      const card = scenarioCards.find((item) => item.id === route.scenarioId);
      return card ? t(card.title) : t("error.load");
    },
    [route, t],
  );
  useEffect(() => {
    document.title = `${title} · Identity Rescue`;
  }, [title]);
  return (
    <Shell onHome={reset}>
      <p
        className="sr-only route-announcement"
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        {title}
      </p>
      {route.kind === "home" && (
        <Home onStart={(id) => navigate(`/case/${id}`)} />
      )}
      {route.kind === "case" && (
        <CasePage scenarioId={route.scenarioId} onReset={reset} />
      )}
      {route.kind === "sources" && <SourcesPage />}
      {route.kind === "privacy" && <PrivacyPage />}
    </Shell>
  );
}
