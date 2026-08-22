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
const rawDir = join(projectRoot, "tmp", "video");
await mkdir(outputDir, { recursive: true });
await mkdir(rawDir, { recursive: true });

const server = spawn(
  "python",
  [
    join(projectRoot, "scripts", "run_local.py"),
    "--port",
    String(port),
    "--database",
    join(projectRoot, "var", "recording.sqlite3"),
  ],
  { cwd: projectRoot, stdio: "ignore", windowsHide: true },
);

async function waitForServer() {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      const response = await fetch(`${baseUrl}/healthz`);
      if (response.ok) return;
    } catch {
      // The server is still starting.
    }
    await new Promise((resolveWait) => setTimeout(resolveWait, 500));
  }
  throw new Error("Local review server did not become healthy");
}

const pause = (page, milliseconds = 650) => page.waitForTimeout(milliseconds);
let browser;
try {
  await waitForServer();
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: rawDir, size: { width: 1280, height: 720 } },
  });
  const page = await context.newPage();
  await page.goto(baseUrl);
  await pause(page, 1000);
  await page.getByRole("button", { name: /selling to a private buyer/i }).click();
  await pause(page);
  await page.getByRole("button", { name: /choose another route/i }).click();
  await page.getByRole("button", { name: /handing it to an authorised dealer/i }).click();
  await pause(page);
  await page.getByRole("button", { name: /use demo vehicle/i }).click();
  await pause(page);
  await page.getByRole("button", { name: /verify and continue/i }).click();
  await page.getByText("INITIATED", { exact: true }).waitFor();
  await pause(page);
  await page.getByLabel(/dealer gstin/i).fill("invalid-gstin");
  await page.getByRole("button", { name: /verify dealer/i }).click();
  await page.getByText("INVALID_GSTIN", { exact: true }).waitFor();
  await pause(page);
  await page.getByRole("button", { name: /use demo dealer/i }).click();
  await page.getByRole("button", { name: /verify dealer/i }).click();
  await page.getByText("DEALER_SELECTED", { exact: true }).waitFor();
  await pause(page);
  await page.getByLabel(/odometer reading/i).fill("12345");
  await page.getByRole("checkbox").nth(0).check();
  await page.getByRole("checkbox").nth(1).check();
  await pause(page);
  await page.getByRole("button", { name: /confirm handover/i }).click();
  await page.getByText("CUSTODY_TRANSFERRED", { exact: true }).waitFor();
  await pause(page, 1200);
  await page.getByRole("button", { name: /details/i }).click();
  await pause(page, 1400);
  const video = page.video();
  await context.close();
  if (!video) throw new Error("Playwright did not create a recording");
  const source = await video.path();
  const destination = join(outputDir, "handover29c-demo.webm");
  await copyFile(source, destination);
  process.stdout.write(`${destination}\n`);
} finally {
  if (browser) await browser.close();
  server.kill();
}
