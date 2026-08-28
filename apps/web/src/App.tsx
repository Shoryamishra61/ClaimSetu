import {
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  ArrowLeft,
  ArrowRight,
  BookOpenText,
  Briefcase,
  CalendarX,
  CheckCircle,
  FileArrowDown,
  FileCode,
  IdentificationCard,
  Info,
  LockKey,
  MagnifyingGlass,
  ShieldCheck,
  UploadSimple,
  UserCircle,
  WarningCircle,
} from "@phosphor-icons/react";

import {
  analyzeScenario,
  analyzeFictionalTestCase,
  getSources,
  parseFictionalTestCase,
  simulateScenario,
  type FictionalTestCase,
  type ScenarioAnalysis,
  type SourceReference,
  type SyntheticRecord,
  type TestCaseResult,
} from "./identityApi";
import { useLang } from "./i18n/LangProvider";

const SCENARIO_ID = "epfo-preflight";
const SESSION_KEY = "claimpath.case.v1";
const BASE_PATH =
  import.meta.env.BASE_URL === "/"
    ? ""
    : import.meta.env.BASE_URL.replace(/\/$/, "");

type JourneyStage = "case" | "diagnosed" | "result";
type Route =
  | { kind: "journey" }
  | { kind: "test-case" }
  | { kind: "sources" }
  | { kind: "privacy" };

function routeFromPath(pathname: string): Route {
  const appPath =
    BASE_PATH && pathname.startsWith(BASE_PATH)
      ? pathname.slice(BASE_PATH.length) || "/"
      : pathname;
  const normalizedPath = appPath.length > 1 ? appPath.replace(/\/+$/, "") : appPath;
  if (normalizedPath === "/sources") return { kind: "sources" };
  if (normalizedPath === "/privacy") return { kind: "privacy" };
  if (normalizedPath === "/test-case") return { kind: "test-case" };
  return { kind: "journey" };
}

function navigate(path: string): void {
  history.pushState({}, "", `${BASE_PATH}${path}` || "/");
  globalThis.dispatchEvent(new PopStateEvent("popstate"));
}

function saveApplied(applied: string[]): void {
  try {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(applied));
  } catch {
    /* The deterministic flow still works without persistence. */
  }
}

function clearJourney(): void {
  try {
    sessionStorage.removeItem(SESSION_KEY);
  } catch {
    /* Already clear enough. */
  }
}

function valueText(value: string | boolean | null): string {
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (value === "NOT_RECORDED") return "—";
  return value ?? "—";
}

function recordByAuthority(
  analysis: ScenarioAnalysis | null,
  authority: string,
): SyntheticRecord | undefined {
  return analysis?.records.find((record) => record.authority === authority);
}

function fieldValue(
  record: SyntheticRecord | undefined,
  field: string,
): string {
  return valueText(record?.fields[field]?.original ?? null);
}

function Shell({ children, onHome }: { children: ReactNode; onHome: () => void }) {
  const { lang, setLang, t } = useLang();
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">{t("a11y.skip")}</a>
      <header className="site-header">
        <div className="header-inner">
          <button
            className="brand"
            type="button"
            onClick={onHome}
            aria-label={`${t("claimpath.name")}: ${t("claimpath.restart")}`}
          >
            <span className="brand-mark" aria-hidden="true">CS</span>
            <span className="brand-copy">
              <strong>{t("claimpath.name")}</strong>
              <small>{t("claimpath.tagline")}</small>
            </span>
          </button>
          <nav className="header-actions" aria-label={t("claimpath.primaryNav")}>
            <span className="fictional-header-note">
              <Info aria-hidden="true" weight="bold" />
              {t("claimpath.fictionalOnly")}
            </span>
            <a className="header-link" href={`${BASE_PATH}/sources`}>
              <BookOpenText aria-hidden="true" />
              {t("nav.sourcesShort")}
            </a>
            <a className="header-link" href={`${BASE_PATH}/test-case`}>
              <FileCode aria-hidden="true" />
              {t("test.nav")}
            </a>
            <div className="language-switch" aria-label={t("nav.language")}>
              <button type="button" aria-pressed={lang === "en"} onClick={() => setLang("en")}>English</button>
              <button type="button" aria-pressed={lang === "hi"} onClick={() => setLang("hi")}>हिन्दी</button>
            </div>
          </nav>
        </div>
      </header>
      {children}
      <footer>
        <div className="footer-links">
          <a href={`${BASE_PATH}/sources`}>{t("nav.sources")}</a>
          <a href={`${BASE_PATH}/privacy`}>{t("nav.privacy")}</a>
          <a href={`${BASE_PATH}/test-case`}>{t("test.nav")}</a>
          <button type="button" onClick={onHome}>{t("claimpath.restart")}</button>
        </div>
        <p>{t("claimpath.disclosure")}</p>
      </footer>
    </div>
  );
}

const progressKeys = [
  ["claimpath.step.diagnose", "claimpath.step.diagnoseHelp"],
  ["claimpath.step.simulate", "claimpath.step.simulateHelp"],
  ["claimpath.step.official", "claimpath.step.officialHelp"],
] as const;

function Progress({ stage }: { stage: JourneyStage }) {
  const { t } = useLang();
  const active = { case: 0, diagnosed: 1, result: 2 }[stage];
  return (
    <nav className="journey-progress" aria-label={t("claimpath.progressLabel")}>
      <ol>
        {progressKeys.map(([label, help], index) => (
          <li
            key={label}
            className={index === active ? "active" : index < active ? "complete" : ""}
            aria-current={index === active ? "step" : undefined}
          >
            <span className="step-number" aria-hidden="true">
              {index < active ? <CheckCircle weight="fill" /> : index + 1}
            </span>
            <span><strong>{t(label)}</strong><small>{t(help)}</small></span>
          </li>
        ))}
      </ol>
    </nav>
  );
}

function FictionalProfile({ status }: { status: string }) {
  const { t } = useLang();
  return (
    <section className="profile-row" aria-label={t("claimpath.profileLabel")}>
      <span className="avatar" aria-hidden="true">RK</span>
      <div className="profile-name">
        <strong>Ravi Kumar</strong>
        <small>{t("claimpath.syntheticUan")}</small>
        <span>XXXX XXXX 4821</span>
      </div>
      <div className="profile-stat"><small>{t("claimpath.balance")}</small><strong>₹45,000</strong></div>
      <div className="profile-stat status-cell"><small>{t("claimpath.status")}</small><strong><span className="status-dot" aria-hidden="true" />{status}</strong></div>
    </section>
  );
}

function RecordsPreview({ analysis }: { analysis: ScenarioAnalysis | null }) {
  const { t } = useLang();
  const aadhaar = recordByAuthority(analysis, "AADHAAR_DEMO");
  const epfo = recordByAuthority(analysis, "EPFO_DEMO");
  const nameAadhaar = analysis ? fieldValue(aadhaar, "name") : "RAVI KUMAR";
  const nameEpfo = analysis ? fieldValue(epfo, "name") : "RAVI K";
  const exitDate = analysis ? fieldValue(epfo, "date_of_exit") : "—";
  return (
    <section className="check-preview" aria-labelledby="checks-heading">
      <h2 id="checks-heading">{t("claimpath.checkTitle")}</h2>
      <div className="record-table" role="table" aria-label={t("claimpath.checkTitle")}>
        <div className="record-head" role="row">
          <span role="columnheader">{t("claimpath.source")}</span>
          <span role="columnheader">{t("claimpath.nameField")}</span>
          <span role="columnheader">{t("claimpath.claimField")}</span>
        </div>
        <div className="record-row" role="row">
          <span className="source-cell" role="cell"><span className="source-icon"><IdentificationCard aria-hidden="true" /></span><strong>{t("claimpath.aadhaarProfile")}</strong></span>
          <span role="cell"><strong>{nameAadhaar}</strong></span>
          <span role="cell">{t("claimpath.nameRecorded")}</span>
        </div>
        <div className="record-row" role="row">
          <span className="source-cell" role="cell"><span className="source-icon"><UserCircle aria-hidden="true" /></span><strong>{t("claimpath.epfoProfile")}</strong></span>
          <span role="cell"><strong>{nameEpfo}</strong><small className="tag visible-tag">{t("claimpath.visibleDifference")}</small></span>
          <span role="cell">{t("claimpath.nameRecorded")}</span>
        </div>
        <div className="record-row" role="row">
          <span className="source-cell" role="cell"><span className="source-icon"><Briefcase aria-hidden="true" /></span><strong>{t("claimpath.serviceHistory")}</strong></span>
          <span role="cell">—</span>
          <span role="cell"><strong>{exitDate === "—" ? t("claimpath.exitMissing") : exitDate}</strong>{exitDate === "—" && <small className="tag blocker-tag">{t("claimpath.possibleBlocker")}</small>}</span>
        </div>
      </div>
    </section>
  );
}

function BeforeAfterPreview({ resolved }: { resolved: boolean }) {
  const { t } = useLang();
  return (
    <section className={`readiness-preview ${resolved ? "resolved" : ""}`} aria-label={t("claimpath.previewLabel")}>
      <div className="before-state"><small>{t("claimpath.before")}</small><strong>{t("claimpath.blockedChecks")}</strong><CalendarX aria-hidden="true" weight="duotone" /><span>{t("claimpath.exitMissing")}</span></div>
      <span className="transition-arrow" aria-hidden="true"><ArrowRight weight="bold" /></span>
      <div className="after-state"><small>{t("claimpath.afterSimulation")}</small><strong>{t("claimpath.modeledPass")}</strong><ShieldCheck aria-hidden="true" weight="fill" /><span>{resolved ? t("claimpath.simulated") : t("claimpath.lockedUntil")}</span></div>
    </section>
  );
}

function CaseStart({
  busy,
  onStart,
}: {
  busy: boolean;
  onStart: () => void;
}) {
  const { t } = useLang();
  return (
    <div className="journey-grid start-grid">
      <section className="story-column">
        <h1>{t("claimpath.hero")}</h1>
        <p className="hero-copy">{t("claimpath.heroBody")}</p>
        <div className="portal-failure" role="note">
          <span>{t("claimpath.currentPortal")}</span>
          <strong>{t("claimpath.currentFailure")}</strong>
          <p>{t("claimpath.currentFailureHelp")}</p>
        </div>
        <FictionalProfile status={t("claimpath.notChecked")} />
        <button className="primary-action" type="button" onClick={onStart} disabled={busy}>
          <MagnifyingGlass aria-hidden="true" weight="bold" />
          {busy ? t("common.loading") : t("claimpath.findBlocker")}
          {!busy && <ArrowRight aria-hidden="true" weight="bold" />}
        </button>
        <p className="browser-note"><LockKey aria-hidden="true" />{t("claimpath.browserNote")}</p>
        <a className="test-data-link" href={`${BASE_PATH}/test-case`}>
          <FileCode aria-hidden="true" />{t("test.entryLink")}<ArrowRight aria-hidden="true" />
        </a>
      </section>
      <aside className="evidence-column">
        <RecordsPreview analysis={null} />
        <BeforeAfterPreview resolved={false} />
        <p className="cause-note"><MagnifyingGlass aria-hidden="true" /> <span><strong>{t("claimpath.causeNotSimilarity")}</strong>{t("claimpath.causeNote")}</span></p>
      </aside>
    </div>
  );
}

function Diagnosis({ analysis, sources, busy, onSimulate }: { analysis: ScenarioAnalysis; sources: SourceReference[]; busy: boolean; onSimulate: () => void }) {
  const { t } = useLang();
  const blocker = analysis.findings.find((finding) => finding.causal);
  const nameFinding = analysis.findings.find((finding) => finding.rule_id === "EPFO-001");
  const matchedSources = sources.filter((source) => blocker?.source_ids.includes(source.source_id));
  return (
    <div className="diagnosis-layout">
      <section className="diagnosis-hero" aria-labelledby="diagnosis-title">
        <div className="status-icon danger"><WarningCircle aria-hidden="true" weight="fill" /></div>
        <div><p className="eyebrow">{t("claimpath.preflightResult")}</p><h1 id="diagnosis-title">{t("claimpath.diagnosisTitle")}</h1><p>{t("claimpath.diagnosisBody")}</p></div>
        <span className="status-pill danger">{t("claimpath.blockedInModel")}</span>
      </section>
      <div className="diagnosis-grid">
        <section className="cause-panel">
          <p className="panel-kicker">{t("claimpath.realBlocker")}</p>
          <div className="cause-heading"><CalendarX aria-hidden="true" weight="duotone" /><div><h2>{t("claimpath.exitMissingTitle")}</h2><p>{t("claimpath.exitMissingBody")}</p></div></div>
          <div className="not-cause"><CheckCircle aria-hidden="true" weight="fill" /><div><strong>{t("claimpath.nameNotCause")}</strong><p>{nameFinding ? t(nameFinding.explanation_key) : t("claimpath.nameNotCauseBody")}</p></div></div>
          {blocker && (
            <details className="technical-evidence">
              <summary>{t("claimpath.viewEvidence")}</summary>
              <div>
                <p><strong>{t("evidence.ruleId")}:</strong> {blocker.rule_id} v{blocker.rule_version}</p>
                <dl>{blocker.inputs.map((input) => <div key={`${input.record_id}-${input.field}`}><dt>{input.label}</dt><dd>{valueText(input.original_value)}</dd></div>)}</dl>
                {matchedSources.map((source) => <a key={source.source_id} href={source.url} target="_blank" rel="noopener noreferrer">{source.title} — {source.publisher}</a>)}
                <p className="prototype-limit">{t("claimpath.evidenceLimit")}</p>
              </div>
            </details>
          )}
          <button className="primary-action" type="button" onClick={onSimulate} disabled={busy}><ShieldCheck aria-hidden="true" weight="bold" />{busy ? t("claimpath.simulating") : t("claimpath.simulateFix")}{!busy && <ArrowRight aria-hidden="true" weight="bold" />}</button>
          <p className="browser-note"><Info aria-hidden="true" />{t("claimpath.simulationOnly")}</p>
        </section>
        <aside className="evidence-column diagnosis-evidence"><RecordsPreview analysis={analysis} /><BeforeAfterPreview resolved={false} /></aside>
      </div>
    </div>
  );
}

function Result({ analysis, sources, onUndo }: { analysis: ScenarioAnalysis; sources: SourceReference[]; onUndo: () => void }) {
  const { t } = useLang();
  const change = analysis.before_after.find((item) => item.action_id === "ACT-B1");
  const umang = sources.find((source) => source.source_id === "SRC-UMANG-001");
  return (
    <div className="result-layout">
      <section className="result-hero" aria-labelledby="result-title">
        <div className="status-icon success"><CheckCircle aria-hidden="true" weight="fill" /></div>
        <div><p className="eyebrow">{t("claimpath.simulationResult")}</p><h1 id="result-title">{t("claimpath.resultTitle")}</h1><p>{t("claimpath.resultBody")}</p></div>
        <span className="status-pill success">{t("claimpath.modeledPass")}</span>
      </section>
      <div className="result-grid">
        <section className="change-summary">
          <h2>{t("claimpath.minimumFix")}</h2><p>{t("claimpath.minimumFixBody")}</p>
          <div className="change-values"><div><small>{t("claimpath.before")}</small><strong>{valueText(change?.before ?? null)}</strong></div><ArrowRight aria-hidden="true" weight="bold" /><div><small>{t("claimpath.after")}</small><strong>{valueText(change?.after ?? null)}</strong></div></div>
          <div className="unchanged-name"><CheckCircle aria-hidden="true" weight="fill" /><span><strong>{t("claimpath.nameLeftAlone")}</strong>{t("claimpath.nameLeftAloneBody")}</span></div>
          <BeforeAfterPreview resolved />
        </section>
        <aside className="handoff-panel">
          <p className="panel-kicker">{t("claimpath.officialNext")}</p><h2>{t("claimpath.handoffTitle")}</h2>
          <ol>{analysis.official_handoff.step_keys.map((key) => <li key={key}>{t(key)}</li>)}</ol>
          <p className="caveat">{t(analysis.official_handoff.caveat_key)}</p>
          <a className="primary-action button-link" href={analysis.official_handoff.official_url} target="_blank" rel="noopener noreferrer"><BookOpenText aria-hidden="true" weight="bold" />{t("claimpath.openEpfo")}<ArrowRight aria-hidden="true" weight="bold" /></a>
          <div className="portal-fallback">
            <strong>{t("claimpath.portalSlowTitle")}</strong>
            <p>{t("claimpath.portalSlowBody")}</p>
            {umang && <a href={umang.url} target="_blank" rel="noopener noreferrer">{t("claimpath.openUmang")} <ArrowRight aria-hidden="true" /></a>}
          </div>
          <button className="secondary-action" type="button" onClick={onUndo}><ArrowLeft aria-hidden="true" />{t("result.undo")}</button>
          <p className="no-real-change"><LockKey aria-hidden="true" />{t("result.noRealChange")}</p>
        </aside>
      </div>
    </div>
  );
}

function ClaimPathJourney() {
  const { t } = useLang();
  const [stage, setStage] = useState<JourneyStage>("case");
  const [analysis, setAnalysis] = useState<ScenarioAnalysis | null>(null);
  const [sources, setSources] = useState<SourceReference[]>([]);
  const [busy, setBusy] = useState(false);
  const [loadError, setLoadError] = useState(false);

  const diagnose = async () => {
    setBusy(true); setLoadError(false);
    try {
      const [next, sourceList] = await Promise.all([analyzeScenario(SCENARIO_ID), getSources()]);
      saveApplied([]); setAnalysis(next); setSources(sourceList); setStage("diagnosed");
    } catch { setLoadError(true); } finally { setBusy(false); }
  };

  const simulate = async () => {
    if (!analysis) return;
    setBusy(true); setLoadError(false);
    try {
      const next = await simulateScenario(SCENARIO_ID, "ACT-B1", analysis.applied_action_ids);
      setAnalysis(next); saveApplied(next.applied_action_ids); setStage("result");
    } catch { setLoadError(true); } finally { setBusy(false); }
  };

  const undo = async () => {
    setBusy(true);
    try { const next = await analyzeScenario(SCENARIO_ID); setAnalysis(next); saveApplied([]); setStage("diagnosed"); }
    finally { setBusy(false); }
  };

  return (
    <main id="main" className="claimpath-page" tabIndex={-1}>
      <Progress stage={stage} />
      {loadError && <p className="page-error" role="alert">{t("common.error")}</p>}
      {stage === "case" && <CaseStart busy={busy} onStart={() => void diagnose()} />}
      {stage === "diagnosed" && analysis && <Diagnosis analysis={analysis} sources={sources} busy={busy} onSimulate={() => void simulate()} />}
      {stage === "result" && analysis && <Result analysis={analysis} sources={sources} onUndo={() => void undo()} />}
      <div className="safety-strip" role="note"><WarningCircle aria-hidden="true" weight="fill" /><span>{t("claimpath.disclosure")}</span></div>
    </main>
  );
}

function SourcesPage() {
  const { t } = useLang();
  const [sources, setSources] = useState<SourceReference[]>([]);
  useEffect(() => { void getSources().then(setSources); }, []);
  const relevant = useMemo(() => sources.filter((source) => source.source_id.startsWith("SRC-EPFO") || source.source_id === "SRC-UMANG-001"), [sources]);
  return (
    <main id="main" className="text-page" tabIndex={-1}>
      <p className="eyebrow">{t("claimpath.name")}</p><h1>{t("sources.title")}</h1><p>{t("sources.body")}</p>
      <div className="source-list">{relevant.map((source) => <article className="source-card" key={source.source_id}><span>{source.source_id}</span><h2>{source.title}</h2><p>{source.publisher}</p><dl><div><dt>{t("sources.proposition")}</dt><dd>{source.proposition}</dd></div><div><dt>{t("sources.checked")}</dt><dd>{source.last_checked_at}</dd></div></dl><a href={source.url} target="_blank" rel="noopener noreferrer">{t("sources.external")} <ArrowRight aria-hidden="true" /></a></article>)}</div>
    </main>
  );
}

function PrivacyPage() {
  const { t } = useLang();
  return (
    <main id="main" className="text-page" tabIndex={-1}>
      <p className="eyebrow">{t("claimpath.name")}</p><h1>{t("privacy.title")}</h1><p>{t("claimpath.privacyBody")}</p><p>{t("privacy.ai")}</p>
      <div className="privacy-principles"><LockKey aria-hidden="true" weight="duotone" /><div><strong>{t("claimpath.disclosure")}</strong><p>{t("claimpath.noteHelp")}</p></div></div>
    </main>
  );
}

const testStatusKeys: Record<TestCaseResult["status"], string> = {
  BLOCKED_DATE_OF_EXIT: "test.status.blocked",
  WAITING_PERIOD_NOT_MET: "test.status.waiting",
  NEEDS_REVIEW: "test.status.review",
  PREREQUISITE_MET: "test.status.ready",
};

function downloadJson(filename: string, value: unknown): void {
  const blob = new Blob([`${JSON.stringify(value, null, 2)}\n`], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function TestCasePage() {
  const { t } = useLang();
  const [testCase, setTestCase] = useState<FictionalTestCase | null>(null);
  const [filename, setFilename] = useState("");
  const [result, setResult] = useState<TestCaseResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [answers, setAnswers] = useState({
    aadhaarName: "",
    epfoName: "",
    relationConfirmed: false,
    exitDate: "",
    waitingMet: false,
    proposedDate: new Date().toISOString().slice(0, 10),
  });

  const acceptValue = (value: unknown, nextFilename: string) => {
    try {
      const parsed = parseFictionalTestCase(value);
      setTestCase(parsed);
      setFilename(nextFilename);
      setResult(null);
      setError("");
    } catch {
      setTestCase(null);
      setResult(null);
      setError(t("test.invalid"));
    }
  };

  const loadBundled = async () => {
    setBusy(true);
    try {
      const response = await fetch(`${import.meta.env.BASE_URL}samples/claimpath-epfo-test-case.json`);
      if (!response.ok) throw new Error("SAMPLE_UNAVAILABLE");
      acceptValue(await response.json(), "claimpath-epfo-test-case.json");
    } catch {
      setError(t("test.unavailable"));
    } finally {
      setBusy(false);
    }
  };

  const readUpload = async (file: File | undefined) => {
    if (!file) return;
    if (file.size > 20_000 || file.type && file.type !== "application/json") {
      setError(t("test.invalid"));
      return;
    }
    try {
      acceptValue(JSON.parse(await file.text()), file.name);
    } catch {
      setError(t("test.invalid"));
    }
  };

  const run = async (applySuggestedFix = false) => {
    if (!testCase) return;
    setBusy(true);
    setError("");
    try {
      setResult(await analyzeFictionalTestCase(testCase, applySuggestedFix));
    } catch {
      setError(t("common.error"));
    } finally {
      setBusy(false);
    }
  };

  const buildFromAnswers = () => {
    const aadhaarName = answers.aadhaarName.trim();
    const epfoName = answers.epfoName.trim();
    const validName = (name: string) =>
      name.length >= 2 && name.length <= 80 && !/\d/.test(name);
    if (!validName(aadhaarName) || !validName(epfoName) || !answers.proposedDate) {
      setError(t("test.formInvalid"));
      return;
    }
    setError("");
    acceptValue(
      {
        schema_version: "claimpath-test-case.v1",
        fictional: true as const,
        aadhaar_linked_name: aadhaarName,
        epfo_name: epfoName,
        name_relation_confirmed: answers.relationConfirmed,
        date_of_exit: answers.exitDate === "" ? null : answers.exitDate,
        proposed_exit_date: answers.proposedDate,
        mark_exit_waiting_period_met: answers.waitingMet,
      },
      t("test.formYourCase"),
    );
  };

  return (
    <main id="main" className="test-page" tabIndex={-1}>
      <section className="test-intro">
        <p className="eyebrow">{t("test.eyebrow")}</p>
        <h1>{t("test.title")}</h1>
        <p>{t("test.body")}</p>
        <div className="test-boundary" role="note">
          <LockKey aria-hidden="true" weight="duotone" />
          <div><strong>{t("test.noRealData")}</strong><p>{t("test.noRealDataBody")}</p></div>
        </div>
      </section>

      <section className="test-workbench" aria-labelledby="test-workbench-title">
        <div className="workbench-heading">
          <div><p className="panel-kicker">{t("test.stepOne")}</p><h2 id="test-workbench-title">{t("test.getCase")}</h2></div>
          <span>{t("test.schema")}</span>
        </div>
        <div className="test-actions">
          <a className="download-action" href={`${import.meta.env.BASE_URL}samples/claimpath-epfo-test-case.json`} download>
            <FileArrowDown aria-hidden="true" />{t("test.download")}
          </a>
          <button className="secondary-action compact-action" type="button" onClick={() => void loadBundled()} disabled={busy}>
            <FileCode aria-hidden="true" />{t("test.loadSample")}
          </button>
          <label className="upload-action">
            <UploadSimple aria-hidden="true" />{t("test.upload")}
            <input type="file" accept="application/json,.json" onChange={(event) => void readUpload(event.target.files?.[0])} />
          </label>
        </div>
        <p className="test-help">{t("test.editHelp")}</p>
        {error && <p className="page-error" role="alert">{error}</p>}

        {testCase && (
          <div className="loaded-test-case">
            <div className="loaded-file"><CheckCircle aria-hidden="true" weight="fill" /><span><strong>{filename}</strong><small>{t("test.validated")}</small></span></div>
            <dl>
              <div><dt>{t("test.aadhaarName")}</dt><dd>{testCase.aadhaar_linked_name}</dd></div>
              <div><dt>{t("test.epfoName")}</dt><dd>{testCase.epfo_name}</dd></div>
              <div><dt>{t("test.exitDate")}</dt><dd>{testCase.date_of_exit ?? t("test.notRecorded")}</dd></div>
              <div><dt>{t("test.waiting")}</dt><dd>{testCase.mark_exit_waiting_period_met ? t("common.yes") : t("common.no")}</dd></div>
            </dl>
            <button className="primary-action" type="button" onClick={() => void run()} disabled={busy}>
              <MagnifyingGlass aria-hidden="true" weight="bold" />{busy ? t("common.loading") : t("test.run")}<ArrowRight aria-hidden="true" />
            </button>
          </div>
        )}
      </section>

      <section className="test-workbench" aria-labelledby="case-form-title">
        <div className="workbench-heading">
          <div><p className="panel-kicker">{t("test.formStep")}</p><h2 id="case-form-title">{t("test.formTitle")}</h2></div>
        </div>
        <p className="test-help">{t("test.formBody")}</p>
        <form
          className="case-form"
          onSubmit={(event) => { event.preventDefault(); buildFromAnswers(); }}
        >
          <label>
            <span>{t("test.formAadhaar")}</span>
            <input
              type="text"
              value={answers.aadhaarName}
              maxLength={80}
              autoComplete="off"
              onChange={(event) => setAnswers({ ...answers, aadhaarName: event.target.value })}
            />
          </label>
          <label>
            <span>{t("test.formEpfo")}</span>
            <input
              type="text"
              value={answers.epfoName}
              maxLength={80}
              autoComplete="off"
              onChange={(event) => setAnswers({ ...answers, epfoName: event.target.value })}
            />
          </label>
          <label className="case-check">
            <input
              type="checkbox"
              checked={answers.relationConfirmed}
              onChange={(event) => setAnswers({ ...answers, relationConfirmed: event.target.checked })}
            />
            <span>{t("test.formRelation")}</span>
          </label>
          <p className="test-help">{t("test.formRelationHelp")}</p>
          <label>
            <span>{t("test.formExit")}</span>
            <input
              type="date"
              value={answers.exitDate}
              onChange={(event) => setAnswers({ ...answers, exitDate: event.target.value })}
            />
          </label>
          <p className="test-help">{t("test.formExitHelp")}</p>
          <label className="case-check">
            <input
              type="checkbox"
              checked={answers.waitingMet}
              onChange={(event) => setAnswers({ ...answers, waitingMet: event.target.checked })}
            />
            <span>{t("test.formWaiting")}</span>
          </label>
          <label>
            <span>{t("test.formProposed")}</span>
            <input
              type="date"
              value={answers.proposedDate}
              onChange={(event) => setAnswers({ ...answers, proposedDate: event.target.value })}
            />
          </label>
          <button className="primary-action" type="submit">
            <MagnifyingGlass aria-hidden="true" weight="bold" />{t("test.formSubmit")}<ArrowRight aria-hidden="true" />
          </button>
        </form>
      </section>

      {result && (
        <section className={`test-result status-${result.status.toLowerCase()}`} aria-live="polite">
          <div className="test-result-heading">
            {result.status === "PREREQUISITE_MET" ? <CheckCircle aria-hidden="true" weight="fill" /> : <WarningCircle aria-hidden="true" weight="fill" />}
            <div><p className="panel-kicker">{t("test.result")}</p><h2>{t(testStatusKeys[result.status])}</h2></div>
            <span className="engine-badge">{result.execution_mode === "FASTAPI_DETERMINISTIC_ENGINE" ? t("test.backendEngine") : t("test.browserEngine")}</span>
          </div>
          <p className="result-action">{result.next_action}</p>
          <div className="trace-list">
            {result.traces.map((trace) => (
              <article key={trace.rule_id}>
                <span className={`trace-status ${trace.status.toLowerCase()}`}>{trace.status}</span>
                <div><strong>{trace.rule_id}</strong><p>{trace.message}</p><small>{trace.source_id}</small></div>
              </article>
            ))}
          </div>
          {result.status === "BLOCKED_DATE_OF_EXIT" && (
            <button className="primary-action" type="button" onClick={() => void run(true)} disabled={busy}>
              <ShieldCheck aria-hidden="true" weight="bold" />{t("test.applyFix")}<ArrowRight aria-hidden="true" />
            </button>
          )}
          <button className="secondary-action compact-action" type="button" onClick={() => downloadJson("claimpath-test-result.json", result)}>
            <FileArrowDown aria-hidden="true" />{t("test.downloadResult")}
          </button>
          <p className="no-real-change"><LockKey aria-hidden="true" />{t("test.resultBoundary")}</p>
        </section>
      )}
    </main>
  );
}

export default function App() {
  const [route, setRoute] = useState<Route>(() => routeFromPath(location.pathname));
  const [journeyKey, setJourneyKey] = useState(0);
  useEffect(() => {
    const update = () => setRoute(routeFromPath(location.pathname));
    globalThis.addEventListener("popstate", update);
    return () => globalThis.removeEventListener("popstate", update);
  }, []);
  const restart = () => { clearJourney(); setJourneyKey((value) => value + 1); navigate("/"); };
  return (
    <Shell onHome={restart}>
      {route.kind === "sources" && <SourcesPage />}
      {route.kind === "privacy" && <PrivacyPage />}
      {route.kind === "test-case" && <TestCasePage />}
      {route.kind === "journey" && <ClaimPathJourney key={journeyKey} />}
    </Shell>
  );
}
