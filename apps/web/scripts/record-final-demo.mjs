import { spawn } from "node:child_process";
import { copyFile, mkdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "playwright";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const webRoot = resolve(scriptDir, "..");
const projectRoot = resolve(webRoot, "../..");
const port = 8134;
const baseUrl = `http://127.0.0.1:${port}`;
const outputDir = join(projectRoot, "output", "video");
const rawDir = join(projectRoot, "tmp", "identity-rescue-final-video");
const timingScale = Number(process.env.DEMO_TIMING_SCALE ?? "1");
await mkdir(outputDir, { recursive: true });
await mkdir(rawDir, { recursive: true });

const server = spawn(
  "python",
  [join(projectRoot, "scripts", "run_local.py"), "--port", String(port)],
  { cwd: projectRoot, stdio: "ignore", windowsHide: true },
);

async function waitForServer() {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      if ((await fetch(`${baseUrl}/healthz`)).ok) return;
    } catch {
      // Server is still starting.
    }
    await new Promise((resolveWait) => setTimeout(resolveWait, 500));
  }
  throw new Error("Local review server did not become healthy");
}

async function startCase(page, scenarioId) {
  await page.getByLabel(/service goal/i).selectOption(scenarioId);
  await page.getByRole("button", { name: /run pre-flight diagnosis/i }).click();
  await page.locator(".status-label").waitFor();
}

async function simulate(page, heading) {
  const option = page
    .getByRole("article")
    .filter({ has: page.getByRole("heading", { name: heading }) });
  await option.getByRole("button", { name: /simulate this route/i }).click();
  await page.getByRole("button", { name: /simulate correction/i }).click();
}

let browser;
try {
  await waitForServer();
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: rawDir, size: { width: 1280, height: 720 } },
  });
  const page = await context.newPage();
  const started = Date.now();
  const holdUntil = async (milliseconds) => {
    const remaining = milliseconds * timingScale - (Date.now() - started);
    if (remaining > 0) await page.waitForTimeout(remaining);
  };

  await page.goto(baseUrl);
  await holdUntil(9_000);
  await startCase(page, "digilocker-dl");
  await holdUntil(22_000);
  await page.getByText(/show the evidence/i).click();
  await page.getByRole("heading", { name: /source basis/i }).first().scrollIntoViewIfNeeded();
  await holdUntil(29_000);
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await holdUntil(35_000);
  await simulate(page, /align the fictional dl source name/i);
  await holdUntil(48_000);
  await page.getByRole("heading", { name: /what you would do next/i }).scrollIntoViewIfNeeded();

  await holdUntil(59_000);
  await page.getByRole("button", { name: /identity rescue: all demo cases/i }).click();
  await startCase(page, "epfo-preflight");
  await holdUntil(65_000);
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await simulate(page, /align the fictional pan display name/i);
  await holdUntil(69_000);
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await simulate(page, /correct the fictional service-history date/i);

  await holdUntil(73_000);
  await page.getByRole("button", { name: /identity rescue: all demo cases/i }).click();
  await startCase(page, "life-event");
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await simulate(page, /use the chosen current name in the fictional dl source/i);
  await page.getByRole("heading", { name: /still different, but not blocking/i }).scrollIntoViewIfNeeded();

  await holdUntil(86_000);
  await page.getByRole("button", { name: "हिन्दी" }).click();
  await page.getByRole("heading", { name: /अभी अलग है/i }).scrollIntoViewIfNeeded();

  await holdUntil(99_000);
  const architectureHtml = `<!doctype html><html><head><meta charset="utf-8"><style>
    *{box-sizing:border-box}body{margin:0;background:#f4f5f1;color:#17211c;font-family:Arial,sans-serif}
    main{width:1120px;margin:0 auto;padding:54px}p.kicker{color:#075746;font-weight:800;letter-spacing:.12em;text-transform:uppercase}
    h1{font-size:44px;margin:10px 0 30px}.flow{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;align-items:center}
    .box{min-height:132px;padding:18px;border:2px solid #b8c4bd;border-radius:14px;background:white;font-weight:800;display:grid;place-items:center;text-align:center}
    .arrow{position:absolute;left:-9999px}.side{margin-top:30px;padding:20px 24px;border-left:6px solid #075746;background:#e8f5ef;font-size:22px}
    .proof{display:flex;gap:24px;margin-top:28px;color:#435048;font-size:19px}.proof strong{color:#075746}
  </style></head><body><main><p class="kicker">How it works</p><h1>Consequential decisions stay deterministic</h1>
  <div class="flow"><div class="box">Fictional citizen case</div><div class="box">Mock authority adapters</div><div class="box">Evidence-preserving comparison</div><div class="box">Versioned rules</div><div class="box">Minimum-impact planner</div><div class="box">Simulation + official handoff</div></div>
  <div class="side"><strong>Codex build role:</strong> specification migration, rule engine, React/FastAPI implementation, accessibility hardening, tests, Docker and deployment. AI cannot change readiness or choose a correction plan.</div>
  <div class="proof"><span><strong>40</strong> backend acceptance cases</span><span><strong>10</strong> browser gates</span><span><strong>3</strong> golden journeys</span><span><strong>0</strong> government calls</span></div>
  </main></body></html>`;
  await page.goto(`data:text/html;charset=utf-8,${encodeURIComponent(architectureHtml)}`);

  await holdUntil(112_000);
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.goto(baseUrl);
  await holdUntil(118_000);

  const video = page.video();
  await context.close();
  if (!video) throw new Error("Playwright did not create a recording");
  const destination = join(outputDir, "identity-rescue-final-visual.webm");
  await copyFile(await video.path(), destination);
  process.stdout.write(`FINAL_VISUAL=${destination}\n`);
} finally {
  if (browser) await browser.close();
  server.kill();
}
