import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  expect: { timeout: 8_000 },
  fullyParallel: false,
  retries: 0,
  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report" }]],
  use: {
    baseURL: "http://127.0.0.1:8130",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  webServer: {
    command: "python ../../scripts/run_local.py --port 8130 --database ../../var/e2e.sqlite3",
    cwd: ".",
    url: "http://127.0.0.1:8130/healthz",
    reuseExistingServer: false,
    timeout: 30_000,
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
