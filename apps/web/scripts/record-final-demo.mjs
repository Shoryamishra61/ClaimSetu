import { spawn } from "node:child_process";
import { copyFile, mkdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const port = 8134;
const baseUrl = `http://127.0.0.1:${port}`;
const outputDir = join(projectRoot, "output", "video");
const rawDir = join(projectRoot, "tmp", "claimpath-final-video");
await mkdir(outputDir, { recursive: true });
await mkdir(rawDir, { recursive: true });
const server = spawn("python", [join(projectRoot, "scripts", "run_local.py"), "--port", String(port)], { cwd: projectRoot, stdio: "ignore", windowsHide: true });

async function waitForServer() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try { if ((await fetch(`${baseUrl}/healthz`)).ok) return; } catch { /* starting */ }
    await new Promise((resolveWait) => setTimeout(resolveWait, 500));
  }
  throw new Error("ClaimPath server did not become healthy");
}

let browser;
try {
  await waitForServer();
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, recordVideo: { dir: rawDir, size: { width: 1280, height: 720 } } });
  const page = await context.newPage();
  const started = Date.now();
  const holdUntil = async (seconds) => { const wait = seconds * 1000 - (Date.now() - started); if (wait > 0) await page.waitForTimeout(wait); };

  await page.goto(baseUrl);
  await holdUntil(9);
  await page.getByRole("button", { name: /load ravi.+fictional case/i }).click();
  await holdUntil(22);
  await page.getByRole("button", { name: /run claim pre-flight/i }).click();
  await holdUntil(35);
  await page.getByText(/view technical evidence/i).click();
  await holdUntil(48);
  await page.getByRole("button", { name: /simulate minimum fix/i }).click();
  await holdUntil(59);

  const architecture = `<!doctype html><html><head><meta charset="utf-8"><style>*{box-sizing:border-box}body{margin:0;background:#f5f7f4;color:#10291f;font-family:Arial,sans-serif}main{padding:48px 64px}small{color:#176b50;font-weight:800;letter-spacing:.13em}h1{font-size:42px;margin:10px 0 34px}.flow{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}.box{min-height:128px;padding:15px;border:1px solid #b8c8c0;border-radius:14px;background:white;display:grid;place-items:center;text-align:center;font-weight:750}.proof{margin-top:30px;padding:22px;border-left:7px solid #176b50;background:#e4f5ed;font-size:21px}.metrics{display:flex;gap:30px;margin-top:24px;color:#485b52}.metrics b{color:#174ea6}</style></head><body><main><small>DETERMINISTIC ARCHITECTURE</small><h1>Evidence in. Minimum safe action out.</h1><div class="flow"><div class="box">Fictional Ravi records</div><div class="box">Original-value evidence model</div><div class="box">Versioned causal rules</div><div class="box">Minimum-cost planner</div><div class="box">Counterfactual recomputation</div><div class="box">Official handoff + fallback</div></div><div class="proof"><b>AI cannot decide readiness or choose the correction.</b> The browser-only note never enters the engine.</div><div class="metrics"><span><b>40</b> backend tests</span><span><b>7</b> UI tests</span><span><b>0</b> government API calls</span><span><b>2</b> official exit routes</span></div></main></body></html>`;
  await page.goto(`data:text/html;charset=utf-8,${encodeURIComponent(architecture)}`);
  await holdUntil(73);
  await page.goto(`${baseUrl}/privacy`);
  await holdUntil(86);
  await page.goto(baseUrl);
  await page.getByRole("button", { name: "हिन्दी" }).click();
  await holdUntil(99);
  await page.getByRole("button", { name: /रवि का काल्पनिक केस खोलें/i }).click();
  await page.getByRole("button", { name: /क्लेम प्री-फ्लाइट चलाएँ/i }).click();
  await page.getByRole("button", { name: /न्यूनतम सुधार का डेमो/i }).click();
  await holdUntil(112);
  await page.locator(".handoff-panel").scrollIntoViewIfNeeded();
  await holdUntil(118);

  const video = page.video();
  await context.close();
  if (!video) throw new Error("Video recording unavailable");
  const destination = join(outputDir, "claimpath-final-visual.webm");
  await copyFile(await video.path(), destination);
  await copyFile(destination, join(outputDir, "identity-rescue-final-visual.webm"));
  process.stdout.write(`FINAL_VISUAL=${destination}\n`);
} finally {
  if (browser) await browser.close();
  server.kill();
}
