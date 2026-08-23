import {
  useEffect,
  useMemo,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import {
  ArrowLeft,
  ArrowRight,
  BookOpenText,
  Briefcase,
  CalendarX,
  CheckCircle,
  FileText,
  IdentificationCard,
  Info,
  LockKey,
  MagnifyingGlass,
  ShieldCheck,
  UserCircle,
  WarningCircle,
} from "@phosphor-icons/react";

import {
  analyzeScenario,
  getSources,
  simulateScenario,
  type ScenarioAnalysis,
  type SourceReference,
  type SyntheticRecord,
} from "./identityApi";
import { useLang } from "./i18n/LangProvider";

const SCENARIO_ID = "epfo-preflight";
const NOTE_KEY = "claimpath.intake.v1";
const SESSION_KEY = "claimpath.case.v1";
const DEFAULT_NOTE =
  "My withdrawal claim could not proceed. I do not know which record is causing it.";
const BASE_PATH =
  import.meta.env.BASE_URL === "/"
    ? ""
    : import.meta.env.BASE_URL.replace(/\/$/, "");

type JourneyStage = "case" | "loaded" | "diagnosed" | "result";
type Route = { kind: "journey" } | { kind: "sources" } | { kind: "privacy" };

function routeFromPath(pathname: string): Route {
  const appPath =
    BASE_PATH && pathname.startsWith(BASE_PATH)
      ? pathname.slice(BASE_PATH.length) || "/"
      : pathname;
  if (appPath === "/sources") return { kind: "sources" };
  if (appPath === "/privacy") return { kind: "privacy" };
  return { kind: "journey" };
}

function navigate(path: string): void {
  history.pushState({}, "", `${BASE_PATH}${path}` || "/");
  globalThis.dispatchEvent(new PopStateEvent("popstate"));
}

function readNote(): string {
  try {
    return sessionStorage.getItem(NOTE_KEY) || DEFAULT_NOTE;
  } catch {
    return DEFAULT_NOTE;
  }
}

function saveNote(note: string): void {
  try {
    sessionStorage.setItem(NOTE_KEY, note);
  } catch {
    /* Browser-only context is optional. */
  }
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
    sessionStorage.removeItem(NOTE_KEY);
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
            <span className="brand-mark" aria-hidden="true">CP</span>
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
            <button className="header-link" type="button" onClick={() => navigate("/sources")}>
              <BookOpenText aria-hidden="true" />
              {t("nav.sourcesShort")}
            </button>
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
          <button type="button" onClick={() => navigate("/sources")}>{t("nav.sources")}</button>
          <button type="button" onClick={() => navigate("/privacy")}>{t("nav.privacy")}</button>
          <button type="button" onClick={onHome}>{t("claimpath.restart")}</button>
        </div>
        <p>{t("claimpath.disclosure")}</p>
      </footer>
    </div>
  );
}

const progressKeys = [
  ["claimpath.step.case", "claimpath.step.caseHelp"],
  ["claimpath.step.diagnose", "claimpath.step.diagnoseHelp"],
  ["claimpath.step.simulate", "claimpath.step.simulateHelp"],
  ["claimpath.step.official", "claimpath.step.officialHelp"],
] as const;

function Progress({ stage }: { stage: JourneyStage }) {
  const { t } = useLang();
  const active = { case: 0, loaded: 1, diagnosed: 2, result: 3 }[stage];
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
  note,
  setNote,
  error,
  busy,
  onSubmit,
}: {
  note: string;
  setNote: (value: string) => void;
  error: string;
  busy: boolean;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const { t } = useLang();
  return (
    <div className="journey-grid start-grid">
      <section className="story-column">
        <h1>{t("claimpath.hero")}</h1>
        <p className="hero-copy">{t("claimpath.heroBody")}</p>
        <FictionalProfile status={t("claimpath.notChecked")} />
        <form className="note-form" onSubmit={onSubmit} noValidate>
          <label htmlFor="claim-note">{t("claimpath.noteLabel")}</label>
          <textarea id="claim-note" maxLength={240} value={note} onChange={(event) => setNote(event.target.value)} aria-describedby="claim-note-help claim-note-count" aria-invalid={Boolean(error)} />
          <div className="note-help"><span id="claim-note-help">{t("claimpath.noteHelp")}</span><span id="claim-note-count">{note.length}/240</span></div>
          {error && <p className="field-error" role="alert">{error}</p>}
          <button className="primary-action" type="submit" disabled={busy}>
            <FileText aria-hidden="true" weight="bold" />
            {busy ? t("common.loading") : t("claimpath.loadCase")}
            {!busy && <ArrowRight aria-hidden="true" weight="bold" />}
          </button>
          <p className="browser-note"><LockKey aria-hidden="true" />{t("claimpath.browserNote")}</p>
        </form>
      </section>
      <aside className="evidence-column">
        <RecordsPreview analysis={null} />
        <BeforeAfterPreview resolved={false} />
        <p className="cause-note"><MagnifyingGlass aria-hidden="true" /> <span><strong>{t("claimpath.causeNotSimilarity")}</strong>{t("claimpath.causeNote")}</span></p>
      </aside>
    </div>
  );
}

function LoadedCase({ analysis, onDiagnose }: { analysis: ScenarioAnalysis; onDiagnose: () => void }) {
  const { t } = useLang();
  return (
    <div className="journey-grid loaded-grid">
      <section className="story-column">
        <p className="eyebrow">{t("claimpath.caseLoaded")}</p>
        <h1>{t("claimpath.loadedTitle")}</h1>
        <p className="hero-copy">{t("claimpath.loadedBody")}</p>
        <FictionalProfile status={t("claimpath.readyToCheck")} />
        <section className="loaded-sources" aria-labelledby="loaded-sources-heading">
          <h2 id="loaded-sources-heading">{t("claimpath.loadedSources")}</h2>
          <ul>
            <li><IdentificationCard aria-hidden="true" />{t("claimpath.aadhaarProfile")}<CheckCircle aria-hidden="true" weight="fill" /></li>
            <li><UserCircle aria-hidden="true" />{t("claimpath.epfoProfile")}<CheckCircle aria-hidden="true" weight="fill" /></li>
            <li><Briefcase aria-hidden="true" />{t("claimpath.serviceHistory")}<CheckCircle aria-hidden="true" weight="fill" /></li>
          </ul>
        </section>
        <button className="primary-action" type="button" onClick={onDiagnose}><MagnifyingGlass aria-hidden="true" weight="bold" />{t("claimpath.runPreflight")}<ArrowRight aria-hidden="true" weight="bold" /></button>
      </section>
      <aside className="evidence-column">
        <RecordsPreview analysis={analysis} />
        <BeforeAfterPreview resolved={false} />
        <p className="cause-note"><Info aria-hidden="true" /> <span><strong>{t("claimpath.noDiagnosisYet")}</strong>{t("claimpath.noDiagnosisBody")}</span></p>
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
  const [note, setNote] = useState(readNote);
  const [noteError, setNoteError] = useState("");
  const [analysis, setAnalysis] = useState<ScenarioAnalysis | null>(null);
  const [sources, setSources] = useState<SourceReference[]>([]);
  const [busy, setBusy] = useState(false);
  const [loadError, setLoadError] = useState(false);

  const loadCase = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = note.trim();
    if (trimmed.length < 10) { setNoteError(t("claimpath.noteTooShort")); return; }
    if (/\b\d{6,}\b/.test(trimmed)) { setNoteError(t("claimpath.noteSensitive")); return; }
    setNoteError(""); setBusy(true); setLoadError(false);
    try {
      const [next, sourceList] = await Promise.all([analyzeScenario(SCENARIO_ID), getSources()]);
      saveNote(trimmed); saveApplied([]); setAnalysis(next); setSources(sourceList); setStage("loaded");
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
      {stage === "case" && <CaseStart note={note} setNote={(value) => { setNote(value); setNoteError(""); }} error={noteError} busy={busy} onSubmit={(event) => void loadCase(event)} />}
      {stage === "loaded" && analysis && <LoadedCase analysis={analysis} onDiagnose={() => setStage("diagnosed")} />}
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
      {route.kind === "journey" && <ClaimPathJourney key={journeyKey} />}
    </Shell>
  );
}
