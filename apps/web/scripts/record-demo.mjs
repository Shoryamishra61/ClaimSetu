import { spawn } from "node:child_process";
import { copyFile, mkdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const webRoot = resolve(scriptDir, "..");
const projectRoot = resolve(webRoot, "../..");
const port = 8131;
const baseUrl = `http://127.0.0.1:${port}`;
const outputDir = join(projectRoot, "output", "video");
const rawDir = join(projectRoot, "tmp", "claimpath-video");
await mkdir(outputDir, { recursive: true });
await mkdir(rawDir, { recursive: true });
const server = spawn("python", [join(projectRoot, "scripts", "run_local.py"), "--port", String(port)], { cwd: projectRoot, stdio: "ignore", windowsHide: true });

async function waitForServer() {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try { if ((await fetch(`${baseUrl}/healthz`)).ok) return; } catch { /* still starting */ }
    await new Promise((resolveWait) => setTimeout(resolveWait, 500));
  }
  throw new Error("Local review server did not become healthy");
}

let browser;
try {
  await waitForServer();
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, recordVideo: { dir: rawDir, size: { width: 1280, height: 720 } } });
  const page = await context.newPage();
  const pause = (milliseconds) => page.waitForTimeout(milliseconds);
  await page.goto(baseUrl);
  await pause(1500);
  await page.getByRole("button", { name: /find what blocks the transfer/i }).click();
  await pause(1800);
  await page.getByText(/view technical evidence/i).click();
  await pause(1400);
  await page.getByRole("button", { name: /simulate minimum fix/i }).click();
  await pause(1800);
  await page.getByRole("button", { name: "हिन्दी" }).click();
  await pause(1400);
  const video = page.video();
  await context.close();
  if (!video) throw new Error("Playwright did not create a recording");
  const destination = join(outputDir, "claimpath-demo.webm");
  await copyFile(await video.path(), destination);
  process.stdout.write(`${destination}\n`);
} finally {
  if (browser) await browser.close();
  server.kill();
}
