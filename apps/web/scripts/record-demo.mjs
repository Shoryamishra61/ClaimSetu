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
const rawDir = join(projectRoot, "tmp", "identity-rescue-video");
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
      const response = await fetch(`${baseUrl}/healthz`);
      if (response.ok) return;
    } catch {
      // The local server is still starting.
    }
    await new Promise((resolveWait) => setTimeout(resolveWait, 500));
  }
  throw new Error("Local review server did not become healthy");
}

const pause = (page, milliseconds = 900) => page.waitForTimeout(milliseconds);

async function startCase(page, heading) {
  const card = page
    .getByRole("article")
    .filter({ has: page.getByRole("heading", { name: heading }) });
  await card.getByRole("button", { name: /try this case/i }).click();
  await pause(page, 1100);
}

async function simulate(page, heading) {
  const option = page
    .getByRole("article")
    .filter({ has: page.getByRole("heading", { name: heading }) });
  await option.getByRole("button", { name: /simulate this route/i }).click();
  await pause(page, 650);
  await page.getByRole("button", { name: /simulate correction/i }).click();
  await pause(page, 1300);
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
  await page.goto(baseUrl);
  await pause(page, 1800);

  await startCase(page, /can't fetch my driving licence/i);
  await page.getByText(/show the evidence/i).click();
  await pause(page, 1300);
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await pause(page, 1200);
  await simulate(page, /align the fictional dl source name/i);
  await page.getByRole("heading", { name: /what you would do next/i }).scrollIntoViewIfNeeded();
  await pause(page, 1500);

  await page.getByRole("button", { name: /identity rescue: all demo cases/i }).click();
  await startCase(page, /pf\/kyc issue/i);
  await page.getByRole("heading", { name: /service-history date blocks this task/i }).scrollIntoViewIfNeeded();
  await pause(page, 1300);
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await simulate(page, /align the fictional pan display name/i);
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await simulate(page, /correct the fictional service-history date/i);

  await page.getByRole("button", { name: /identity rescue: all demo cases/i }).click();
  await startCase(page, /name or address changed/i);
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await simulate(page, /use the chosen current name in the fictional dl source/i);
  await page.getByRole("heading", { name: /still different, but not blocking/i }).scrollIntoViewIfNeeded();
  await pause(page, 1400);

  await page.getByRole("button", { name: "हिन्दी" }).click();
  await pause(page, 1600);

  const video = page.video();
  await context.close();
  if (!video) throw new Error("Playwright did not create a recording");
  const source = await video.path();
  const destination = join(outputDir, "identity-rescue-demo.webm");
  await copyFile(source, destination);
  process.stdout.write(`${destination}\n`);
} finally {
  if (browser) await browser.close();
  server.kill();
}
