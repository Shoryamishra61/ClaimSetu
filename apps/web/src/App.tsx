import { useEffect, useMemo, useState, type FormEvent, type ReactNode } from "react";

import {
  CustodyApiError,
  form29cUrl,
  getCustodyCase,
  initiateCustodyCase,
  setCustodyState,
  verifyCustodyDealer,
  verifyCustodyVehicle,
  type CustodyCase,
  type DealerFixture,
} from "./custodyApi";
import { useLang } from "./i18n/LangProvider";

const CASE_STORAGE_KEY = "h29c.custody.case.v1";
const DEMO_VEHICLE = { vehicleNo: "DL-1CA-1234", chassisSuffix: "56789" };
const DEMO_DEALER_GSTIN = "07AAAAA1111A1Z1";

type RouteChoice = "dealer" | "private" | null;
type SyncMode = "connecting" | "live" | "polling";

function safeStoredCaseId(): string | null {
  try {
    return sessionStorage.getItem(CASE_STORAGE_KEY);
  } catch {
    return null;
  }
}

function rememberCase(caseId: string | null): void {
  try {
    if (caseId) sessionStorage.setItem(CASE_STORAGE_KEY, caseId);
    else sessionStorage.removeItem(CASE_STORAGE_KEY);
  } catch {
    // Refresh persistence is a convenience; the workflow still works without it.
  }
}

function syncUrl(caseId: string): string {
  const protocol = globalThis.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${globalThis.location.host}/api/v1/sync/${encodeURIComponent(caseId)}`;
}

function useCustodySync(
  caseId: string | null,
  onSnapshot: (snapshot: CustodyCase) => void,
): SyncMode {
  const [mode, setMode] = useState<SyncMode>("connecting");

  useEffect(() => {
    if (!caseId) return;
    let closed = false;
    let socket: WebSocket | null = null;
    let reconnect: ReturnType<typeof setTimeout> | null = null;
    let attempts = 0;

    const refresh = async (): Promise<void> => {
      try {
        onSnapshot(await getCustodyCase(caseId));
      } catch {
        // A later poll or socket snapshot can recover without erasing good state.
      }
    };
    const poll = setInterval(() => void refresh(), 2500);
    void refresh();

    const connect = (): void => {
      if (closed) return;
      try {
        socket = new WebSocket(syncUrl(caseId));
      } catch {
        setMode("polling");
        return;
      }
      socket.onopen = () => {
        attempts = 0;
        setMode("live");
      };
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(String(event.data)) as {
            type?: string;
            case?: CustodyCase;
          };
          if (data.type === "CUSTODY_CASE_SNAPSHOT" && data.case) onSnapshot(data.case);
        } catch {
          // Ignore malformed transport frames; REST remains authoritative.
        }
      };
      socket.onerror = () => setMode("polling");
      socket.onclose = () => {
        if (closed) return;
        setMode("polling");
        attempts += 1;
        reconnect = setTimeout(connect, Math.min(15_000, 500 * 2 ** attempts));
      };
    };
    connect();
    return () => {
      closed = true;
      clearInterval(poll);
      if (reconnect) clearTimeout(reconnect);
      if (socket) {
        socket.onclose = null;
        socket.close();
      }
    };
  }, [caseId, onSnapshot]);

  return mode;
}

function Notice({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="notice" role="note">
      <strong>{title}</strong>
      <div>{children}</div>
    </div>
  );
}

function ErrorNotice({ error }: { error: CustodyApiError | null }) {
  if (!error) return null;
  return (
    <div className="error-notice" role="alert">
      <strong>{error.code}</strong>
      <span>{error.message}</span>
    </div>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="summary-row">
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function Progress({ active, hi }: { active: number; hi: boolean }) {
  const labels = hi
    ? ["वाहन", "डीलर", "सुपुर्दगी", "रिकॉर्ड"]
    : ["Vehicle", "Dealer", "Handover", "Record"];
  return (
    <nav className="progress" aria-label={hi ? "हस्तांतरण की प्रगति" : "Handover progress"}>
      <ol>
        {labels.map((label, index) => {
          const complete = index < active;
          const current = index === active;
          return (
            <li key={label} className={complete ? "complete" : current ? "current" : "future"}>
              <span className="step-number" aria-hidden="true">
                {complete ? "✓" : index + 1}
              </span>
              <span className="step-label">{label}</span>
              <span className="step-line" aria-hidden="true" />
              <span className="sr-only">
                {complete ? (hi ? "पूर्ण" : "complete") : current ? (hi ? "वर्तमान" : "current") : ""}
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export default function App() {
  const { lang, setLang } = useLang();
  const hi = lang === "hi";
  const pick = (en: string, hindi: string): string => (hi ? hindi : en);
  const [route, setRoute] = useState<RouteChoice>(() => (safeStoredCaseId() ? "dealer" : null));
  const [storedCaseId, setStoredCaseId] = useState<string | null>(safeStoredCaseId);
  const [caseData, setCaseData] = useState<CustodyCase | null>(null);
  const [vehicleNo, setVehicleNo] = useState("");
  const [chassisSuffix, setChassisSuffix] = useState("");
  const [gstin, setGstin] = useState("");
  const [dealer, setDealer] = useState<DealerFixture | null>(null);
  const [odometer, setOdometer] = useState("");
  const [sellerConfirmed, setSellerConfirmed] = useState(false);
  const [dealerConfirmed, setDealerConfirmed] = useState(false);
  const [error, setError] = useState<CustodyApiError | null>(null);
  const [busy, setBusy] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);

  const applySnapshot = useMemo(
    () => (next: CustodyCase) => {
      setCaseData((current) =>
        !current || next.updated_at >= current.updated_at ? next : current,
      );
    },
    [],
  );
  const syncMode = useCustodySync(caseData?.case_id ?? storedCaseId, applySnapshot);

  useEffect(() => {
    const restored = safeStoredCaseId();
    if (!restored) return;
    getCustodyCase(restored)
      .then((next) => {
        setCaseData(next);
        setRoute("dealer");
      })
      .catch(() => {
        rememberCase(null);
        setStoredCaseId(null);
      });
  }, []);

  useEffect(() => {
    if (!detailsOpen) return;
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") setDetailsOpen(false);
    };
    document.addEventListener("keydown", close);
    return () => document.removeEventListener("keydown", close);
  }, [detailsOpen]);

  const activeStep = !caseData
    ? 0
    : caseData.state === "INITIATED"
      ? 1
      : caseData.state === "DEALER_SELECTED"
        ? 2
        : 3;

  const useDemoVehicle = (): void => {
    setVehicleNo(DEMO_VEHICLE.vehicleNo);
    setChassisSuffix(DEMO_VEHICLE.chassisSuffix);
    setError(null);
  };

  const handleVehicle = async (event: FormEvent): Promise<void> => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const found = await verifyCustodyVehicle(vehicleNo, chassisSuffix);
      const created = await initiateCustodyCase(found);
      setCaseData(created);
      rememberCase(created.case_id);
      setStoredCaseId(created.case_id);
    } catch (caught) {
      setError(
        caught instanceof CustodyApiError
          ? caught
          : new CustodyApiError("UNKNOWN_ERROR", "This step could not be completed.", "यह चरण पूरा नहीं हो सका।"),
      );
    } finally {
      setBusy(false);
    }
  };

  const handleDealer = async (event: FormEvent): Promise<void> => {
    event.preventDefault();
    if (!caseData) return;
    setBusy(true);
    setError(null);
    try {
      const found = await verifyCustodyDealer({ gstin });
      setDealer(found);
      if (!found.can_continue) {
        throw new CustodyApiError(
          "DEALER_NOT_ACTIVE",
          "This fictional dealer is not active. Choose another demo dealer.",
          "यह काल्पनिक डीलर सक्रिय नहीं है। दूसरा डेमो डीलर चुनें।",
        );
      }
      setCaseData(
        await setCustodyState(caseData.case_id, {
          state: "DEALER_SELECTED",
          dealer_id: found.dealer_id,
        }),
      );
    } catch (caught) {
      setError(
        caught instanceof CustodyApiError
          ? caught
          : new CustodyApiError("UNKNOWN_ERROR", "This step could not be completed.", "यह चरण पूरा नहीं हो सका।"),
      );
    } finally {
      setBusy(false);
    }
  };

  const handleHandover = async (event: FormEvent): Promise<void> => {
    event.preventDefault();
    if (!caseData) return;
    setBusy(true);
    setError(null);
    try {
      const reading = Number(odometer);
      if (!Number.isInteger(reading) || reading <= 0) {
        throw new CustodyApiError(
          "INVALID_ODOMETER",
          "Odometer reading must be a whole number greater than zero.",
          "ओडोमीटर रीडिंग शून्य से अधिक पूर्ण संख्या होनी चाहिए।",
        );
      }
      setCaseData(
        await setCustodyState(caseData.case_id, {
          state: "CUSTODY_TRANSFERRED",
          odometer_reading: reading,
          seller_confirmed: sellerConfirmed,
          dealer_confirmed: dealerConfirmed,
        }),
      );
    } catch (caught) {
      setError(
        caught instanceof CustodyApiError
          ? caught
          : new CustodyApiError("UNKNOWN_ERROR", "This step could not be completed.", "यह चरण पूरा नहीं हो सका।"),
      );
    } finally {
      setBusy(false);
    }
  };

  const startAgain = (): void => {
    rememberCase(null);
    setRoute(null);
    setCaseData(null);
    setStoredCaseId(null);
    setDealer(null);
    setVehicleNo("");
    setChassisSuffix("");
    setGstin("");
    setOdometer("");
    setSellerConfirmed(false);
    setDealerConfirmed(false);
    setError(null);
  };

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        {pick("Skip to main content", "मुख्य सामग्री पर जाएँ")}
      </a>
      <div className="prototype-banner" role="note">
        <div>
          <span className="info-mark" aria-hidden="true">i</span>
          <span>
            <strong>{pick("Independent prototype", "स्वतंत्र प्रोटोटाइप")}</strong>
            {pick(" - simulated government integrations - fictional data.", " - सरकारी एकीकरण सिम्युलेटेड हैं - काल्पनिक डेटा।")}
          </span>
        </div>
      </div>

      <header className="site-header">
        <div className="header-inner">
          <div className="brand-block">
            <span className="document-mark" aria-hidden="true">29C</span>
            <span>
              <strong>Handover29C</strong>
              <small>{pick("Custody record prototype", "सुपुर्दगी रिकॉर्ड प्रोटोटाइप")}</small>
            </span>
            <span className="prototype-chip">{pick("Prototype", "प्रोटोटाइप")}</span>
          </div>
          <div className="header-actions">
            <div className="language-switch" aria-label={pick("Language selection", "भाषा चयन")}>
              <button type="button" aria-pressed={!hi} onClick={() => setLang("en")}>English</button>
              <button type="button" aria-pressed={hi} onClick={() => setLang("hi")}>हिन्दी</button>
            </div>
            <button className="secondary compact" type="button" onClick={() => setDetailsOpen(true)}>
              {pick("Details", "विवरण")}
            </button>
          </div>
        </div>
      </header>

      <main id="main-content" className="main-content" tabIndex={-1}>
        <div className="intro">
          <p className="eyebrow">{pick("Prepare a custody record", "सुपुर्दगी रिकॉर्ड तैयार करें")}</p>
          <h1>{pick("Vehicle handover to a dealer", "डीलर को वाहन सुपुर्दगी")}</h1>
          <p>{pick("A guided demo for preparing a fictional Form 29C record. Review each fact before moving forward.", "काल्पनिक फ़ॉर्म 29C रिकॉर्ड तैयार करने का निर्देशित डेमो। आगे बढ़ने से पहले हर तथ्य जाँचें।")}</p>
        </div>

        {route === "dealer" && <Progress active={activeStep} hi={hi} />}
        <div className="live-region" aria-live="polite" aria-atomic="true">
          {busy ? pick("Working on this step.", "यह चरण पूरा किया जा रहा है।") : error?.message ?? ""}
        </div>

        {route === null && (
          <section className="task-card route-card" aria-labelledby="route-title">
            <div className="card-heading">
              <div>
                <span className="state-chip neutral">{pick("Choose route", "मार्ग चुनें")}</span>
                <h2 id="route-title">{pick("What are you doing with the vehicle?", "आप वाहन के साथ क्या कर रहे हैं?")}</h2>
              </div>
            </div>
            <div className="route-options">
              <button type="button" className="route-option" onClick={() => setRoute("dealer")}>
                <span className="option-index" aria-hidden="true">A</span>
                <span><strong>{pick("Handing it to an authorised dealer", "अधिकृत डीलर को सौंप रहे हैं")}</strong><small>{pick("Prepare a fictional custody record through this prototype.", "इस प्रोटोटाइप से काल्पनिक सुपुर्दगी रिकॉर्ड तैयार करें।")}</small></span>
              </button>
              <button type="button" className="route-option" onClick={() => setRoute("private")}>
                <span className="option-index" aria-hidden="true">B</span>
                <span><strong>{pick("Selling to a private buyer", "निजी खरीदार को बेच रहे हैं")}</strong><small>{pick("A different statutory route, not covered here.", "यह अलग वैधानिक मार्ग है, यहाँ शामिल नहीं है।")}</small></span>
              </button>
            </div>
          </section>
        )}

        {route === "private" && (
          <section className="task-card" aria-labelledby="scope-title">
            <span className="state-chip warning">{pick("Out of scope", "कार्यक्षेत्र से बाहर")}</span>
            <h2 id="scope-title">{pick("Private-buyer transfer is a different process", "निजी खरीदार को हस्तांतरण एक अलग प्रक्रिया है")}</h2>
            <Notice title={pick("Why this stops here", "यहाँ क्यों रुकता है")}>
              <p>{pick("Form 29C in this prototype is limited to custody handover to a fictional authorised dealer. It must not be reused for a private sale.", "इस प्रोटोटाइप में फ़ॉर्म 29C केवल काल्पनिक अधिकृत डीलर को सुपुर्दगी तक सीमित है। निजी बिक्री के लिए इसका उपयोग न करें।")}</p>
            </Notice>
            <button className="secondary" type="button" onClick={() => setRoute(null)}>{pick("Choose another route", "दूसरा मार्ग चुनें")}</button>
          </section>
        )}

        {route === "dealer" && !caseData && (
          <section className="task-card" aria-labelledby="vehicle-title">
            <div className="card-heading">
              <div><span className="state-chip neutral">DRAFT</span><h2 id="vehicle-title">{pick("Enter vehicle details", "वाहन विवरण दर्ज करें")}</h2><p>{pick("Use one of the fictional fixtures. No live registry is queried.", "काल्पनिक फ़िक्स्चर का उपयोग करें। कोई लाइव रजिस्ट्री नहीं जाँची जाती।")}</p></div>
            </div>
            <Notice title={pick("Prototype boundary", "प्रोटोटाइप सीमा")}><p>{pick("Do not enter real registration, chassis, mobile, or identity information.", "वास्तविक पंजीकरण, चेसिस, मोबाइल या पहचान जानकारी दर्ज न करें।")}</p></Notice>
            <ErrorNotice error={error} />
            <form onSubmit={(event) => void handleVehicle(event)} aria-busy={busy}>
              <div className="field-grid">
                <label><span>{pick("Registration plate", "पंजीकरण संख्या")}</span><input required value={vehicleNo} onChange={(event) => setVehicleNo(event.target.value)} autoComplete="off" placeholder="DL-1CA-1234" /><small>{pick("Fictional example: DL-1CA-1234", "काल्पनिक उदाहरण: DL-1CA-1234")}</small></label>
                <label><span>{pick("Chassis suffix", "चेसिस के अंतिम अक्षर")}</span><input required minLength={3} value={chassisSuffix} onChange={(event) => setChassisSuffix(event.target.value)} autoComplete="off" placeholder="56789" /><small>{pick("Use the final 5 characters in this demo.", "इस डेमो में अंतिम 5 अक्षर उपयोग करें।")}</small></label>
              </div>
              <div className="form-actions"><button className="secondary" type="button" onClick={useDemoVehicle}>{pick("Use demo vehicle", "डेमो वाहन चुनें")}</button><button className="primary" disabled={busy} type="submit">{busy ? pick("Checking...", "जाँच जारी...") : pick("Verify and continue", "सत्यापित कर आगे बढ़ें")}</button></div>
            </form>
          </section>
        )}

        {route === "dealer" && caseData?.state === "INITIATED" && (
          <section className="task-card" aria-labelledby="dealer-title">
            <div className="card-heading"><div><span className="state-chip active">INITIATED</span><h2 id="dealer-title">{pick("Select the fictional dealer", "काल्पनिक डीलर चुनें")}</h2><p>{pick("The dealer must be active in the local simulated registry.", "स्थानीय सिम्युलेटेड रजिस्ट्री में डीलर सक्रिय होना चाहिए।")}</p></div></div>
            <dl className="summary"><SummaryRow label={pick("Vehicle", "वाहन")} value={caseData.vehicle_no} /><SummaryRow label={pick("Seller", "विक्रेता")} value={caseData.seller_name} /></dl>
            <ErrorNotice error={error} />
            <form onSubmit={(event) => void handleDealer(event)} aria-busy={busy}>
              <label><span>{pick("Dealer GSTIN", "डीलर GSTIN")}</span><input required value={gstin} onChange={(event) => setGstin(event.target.value)} autoComplete="off" placeholder={DEMO_DEALER_GSTIN} /><small>{pick("Required format is validated before lookup.", "खोज से पहले आवश्यक प्रारूप की जाँच होती है।")}</small></label>
              <div className="form-actions"><button className="secondary" type="button" onClick={() => { setGstin(DEMO_DEALER_GSTIN); setError(null); }}>{pick("Use demo dealer", "डेमो डीलर चुनें")}</button><button className="primary" disabled={busy} type="submit">{busy ? pick("Checking...", "जाँच जारी...") : pick("Verify dealer", "डीलर सत्यापित करें")}</button></div>
            </form>
          </section>
        )}

        {route === "dealer" && caseData?.state === "DEALER_SELECTED" && (
          <section className="task-card" aria-labelledby="handover-title">
            <div className="card-heading"><div><span className="state-chip active">DEALER_SELECTED</span><h2 id="handover-title">{pick("Record the physical handover", "भौतिक सुपुर्दगी दर्ज करें")}</h2><p>{pick("Both people confirm the same fictional custody details on this device.", "दोनों व्यक्ति इस डिवाइस पर समान काल्पनिक सुपुर्दगी विवरण की पुष्टि करते हैं।")}</p></div></div>
            <dl className="summary"><SummaryRow label={pick("Vehicle", "वाहन")} value={caseData.vehicle_no} /><SummaryRow label={pick("Seller", "विक्रेता")} value={caseData.seller_name} /><SummaryRow label={pick("Dealer", "डीलर")} value={caseData.dealer_name ?? dealer?.business_name ?? "-"} /><SummaryRow label="GSTIN" value={caseData.dealer_gstin ?? "-"} /></dl>
            <Notice title={pick("What confirmation means", "पुष्टि का अर्थ")}><p>{pick("It records agreement inside this prototype only. It is not an e-signature, portal submission, or government acknowledgement.", "यह केवल इस प्रोटोटाइप में सहमति दर्ज करता है। यह ई-हस्ताक्षर, पोर्टल सबमिशन या सरकारी पावती नहीं है।")}</p></Notice>
            <ErrorNotice error={error} />
            <form onSubmit={(event) => void handleHandover(event)} aria-busy={busy}>
              <label><span>{pick("Odometer reading (km)", "ओडोमीटर रीडिंग (किमी)")}</span><input required min={1} step={1} inputMode="numeric" type="number" value={odometer} onChange={(event) => setOdometer(event.target.value)} /><small>{pick("Enter a whole number greater than zero.", "शून्य से अधिक पूर्ण संख्या दर्ज करें।")}</small></label>
              <fieldset className="confirmations"><legend>{pick("Both confirmations are required", "दोनों पुष्टियाँ आवश्यक हैं")}</legend><label className="check-row"><input type="checkbox" checked={sellerConfirmed} onChange={(event) => setSellerConfirmed(event.target.checked)} /><span>{pick("The fictional seller confirms physical custody was handed over.", "काल्पनिक विक्रेता भौतिक सुपुर्दगी की पुष्टि करता है।")}</span></label><label className="check-row"><input type="checkbox" checked={dealerConfirmed} onChange={(event) => setDealerConfirmed(event.target.checked)} /><span>{pick("The fictional dealer confirms physical custody was received.", "काल्पनिक डीलर भौतिक सुपुर्दगी प्राप्त होने की पुष्टि करता है।")}</span></label></fieldset>
              <div className="form-actions end"><button className="primary" disabled={busy || !sellerConfirmed || !dealerConfirmed} type="submit">{busy ? pick("Preparing record...", "रिकॉर्ड तैयार हो रहा है...") : pick("Confirm handover and prepare record", "सुपुर्दगी की पुष्टि कर रिकॉर्ड तैयार करें")}</button></div>
            </form>
          </section>
        )}

        {route === "dealer" && caseData?.state === "CUSTODY_TRANSFERRED" && (
          <section className="task-card record-card" aria-labelledby="record-title">
            <div className="record-mark" aria-hidden="true">✓</div>
            <span className="state-chip complete-state">CUSTODY_TRANSFERRED</span>
            <h2 id="record-title">{pick("Prototype custody record prepared", "प्रोटोटाइप सुपुर्दगी रिकॉर्ड तैयार है")}</h2>
            <p>{pick("The fictional handover facts were saved and a pre-filled PDF was generated locally.", "काल्पनिक सुपुर्दगी तथ्य सहेजे गए और प्री-फिल्ड PDF स्थानीय रूप से बनाया गया।")}</p>
            <Notice title={pick("Not a portal acknowledgement", "पोर्टल पावती नहीं")}><p>{pick("This PDF was not submitted to a government portal and has no portal acknowledgement number or claimed legal effect.", "यह PDF किसी सरकारी पोर्टल पर जमा नहीं किया गया और इसकी कोई पोर्टल पावती संख्या या दावा किया गया कानूनी प्रभाव नहीं है।")}</p></Notice>
            <dl className="summary"><SummaryRow label={pick("Vehicle", "वाहन")} value={caseData.vehicle_no} /><SummaryRow label={pick("Seller", "विक्रेता")} value={caseData.seller_name} /><SummaryRow label={pick("Dealer", "डीलर")} value={caseData.dealer_name ?? "-"} /><SummaryRow label={pick("Odometer", "ओडोमीटर")} value={`${caseData.odometer_reading ?? "-"} km`} /><SummaryRow label={pick("Case reference", "केस संदर्भ")} value={caseData.case_id} /></dl>
            <div className="form-actions end"><button className="secondary" type="button" onClick={startAgain}>{pick("Start another demo", "दूसरा डेमो शुरू करें")}</button><a className="primary button-link" href={form29cUrl(caseData.case_id)} download>{pick("Download prototype Form 29C PDF", "प्रोटोटाइप फ़ॉर्म 29C PDF डाउनलोड करें")}</a></div>
          </section>
        )}

        {route === "dealer" && caseData && (
          <p className="sync-note">{pick("Saved case", "सहेजा गया केस")}: <code>{caseData.case_id}</code> · {syncMode === "live" ? pick("live updates", "लाइव अपडेट") : pick("reliable polling", "विश्वसनीय पोलिंग")}</p>
        )}
      </main>

      <footer><p>{pick("Independent hackathon prototype. No live government integrations.", "स्वतंत्र हैकाथॉन प्रोटोटाइप। कोई लाइव सरकारी एकीकरण नहीं।")}</p></footer>

      {detailsOpen && (
        <div className="drawer-backdrop" onMouseDown={() => setDetailsOpen(false)}>
          <aside className="details-drawer" role="dialog" aria-modal="true" aria-labelledby="details-title" onMouseDown={(event) => event.stopPropagation()}>
            <div className="drawer-heading"><h2 id="details-title">{pick("Prototype details", "प्रोटोटाइप विवरण")}</h2><button type="button" className="icon-button" aria-label={pick("Close details", "विवरण बंद करें")} onClick={() => setDetailsOpen(false)}>×</button></div>
            <h3>{pick("What works", "क्या काम करता है")}</h3><ul><li>{pick("Transactional SQLite custody workflow", "ट्रांजैक्शनल SQLite सुपुर्दगी वर्कफ़्लो")}</li><li>{pick("Fictional vehicle and dealer verification", "काल्पनिक वाहन और डीलर सत्यापन")}</li><li>{pick("Text-extractable prototype PDF", "टेक्स्ट निकालने योग्य प्रोटोटाइप PDF")}</li><li>{pick("WebSocket updates with REST polling fallback", "REST पोलिंग फ़ॉलबैक के साथ WebSocket अपडेट")}</li></ul>
            <h3>{pick("What is simulated", "क्या सिम्युलेटेड है")}</h3><ul><li>{pick("Every registry record and person", "हर रजिस्ट्री रिकॉर्ड और व्यक्ति")}</li><li>{pick("Every dealer status", "हर डीलर स्थिति")}</li><li>{pick("The complete government integration boundary", "पूरी सरकारी एकीकरण सीमा")}</li></ul>
            <h3>{pick("What this does not do", "यह क्या नहीं करता")}</h3><p>{pick("It does not file Form 29C, create a portal acknowledgement, verify identity, transfer ownership, or change legal liability.", "यह फ़ॉर्म 29C दाखिल नहीं करता, पोर्टल पावती नहीं बनाता, पहचान सत्यापित नहीं करता, स्वामित्व हस्तांतरित नहीं करता और कानूनी दायित्व नहीं बदलता।")}</p>
            <p className="source-line"><strong>{pick("Policy anchor", "नीति आधार")}:</strong> CMVR Gazette G.S.R. 901(E), 22 December 2022. The repository evidence ledger controls claims.</p>
            <button type="button" className="primary full" onClick={() => setDetailsOpen(false)}>{pick("Close", "बंद करें")}</button>
          </aside>
        </div>
      )}
    </div>
  );
}
