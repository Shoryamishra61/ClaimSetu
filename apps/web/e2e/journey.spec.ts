import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function loadRavi(page: Page) {
  await page.getByRole("button", { name: /load ravi.+fictional case/i }).click();
  await expect(page.getByRole("button", { name: /run claim pre-flight/i })).toBeVisible();
}

async function diagnose(page: Page) {
  await loadRavi(page);
  await page.getByRole("button", { name: /run claim pre-flight/i }).click();
  await expect(page.getByText(/blocked in this model/i)).toBeVisible();
}

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => sessionStorage.clear());
  await page.reload();
});

test("focused entry is safe, keyboard reachable, and accessible", async ({ page }) => {
  await expect(page).toHaveTitle(/ClaimPath/);
  await expect(page.getByRole("heading", { name: /ravi.+45,000 pf withdrawal is at risk/i })).toBeVisible();
  await expect(page.getByText(/fictional demo.+not epfo/i)).toBeVisible();
  await expect(page.getByText(/do not enter aadhaar/i)).toBeVisible();
  await expect(page.getByLabel(/what happened/i)).toBeEditable();
  await expect(page.locator('meta[http-equiv="Content-Security-Policy"]')).toHaveAttribute("content", /object-src 'none'/);
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: /skip to main content/i })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main")).toBeFocused();
  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(accessibility.violations.filter((item) => item.impact === "serious" || item.impact === "critical")).toEqual([]);
});

test("four-click journey finds the causal blocker and proves the minimum fix", async ({ page }) => {
  await loadRavi(page);
  await expect(page.getByText(/ravi k/i).first()).toBeVisible();
  await page.getByRole("button", { name: /run claim pre-flight/i }).click();
  await expect(page.getByText(/blocked in this model/i)).toBeVisible();
  await expect(page.getByRole("heading", { name: /date of exit is missing/i })).toBeVisible();
  await expect(page.getByText(/do not change the name for this blocker/i)).toBeVisible();
  await page.getByText(/view technical evidence/i).click();
  await expect(page.getByText(/prototype simulation/i).first()).toBeVisible();
  await page.getByRole("button", { name: /simulate minimum fix/i }).click();
  await expect(page.getByText(/modeled checks pass/i)).toBeVisible();
  await expect(page.getByText(/not a guarantee of claim approval/i)).toBeVisible();
  const official = page.getByRole("link", { name: /open epfo member portal/i });
  await expect(official).toHaveAttribute("href", /unifiedportal-mem\.epfindia\.gov\.in/);
  await expect(official).toHaveAttribute("rel", "noopener noreferrer");
  await expect(page.getByRole("link", { name: /use official umang epfo services/i })).toHaveAttribute("href", /web\.umang\.gov\.in/);
});

test("sensitive identifiers are rejected before any API request", async ({ page }) => {
  let requests = 0;
  page.on("request", (request) => { if (request.url().includes("/api/v1/identity/")) requests += 1; });
  await page.getByLabel(/what happened/i).fill("My Aadhaar is 123456789012");
  await page.getByRole("button", { name: /load ravi.+fictional case/i }).click();
  await expect(page.getByText(/remove long identification numbers/i)).toBeVisible();
  expect(requests).toBe(0);
});

test("note stays browser-only and is not sent in the diagnosis payload", async ({ page }) => {
  const note = "My transfer claim stops after selecting the previous job.";
  let body = "";
  page.on("request", (request) => { if (request.url().includes("/analyze")) body = request.postData() ?? ""; });
  await page.getByLabel(/what happened/i).fill(note);
  await diagnose(page);
  expect(body).not.toBe("");
  expect(body).not.toContain(note);
  expect(await page.evaluate(() => sessionStorage.getItem("claimpath.intake.v1"))).toContain(note);
});

test("Hindi journey has no leaked translation keys", async ({ page }) => {
  await page.getByRole("button", { name: "हिन्दी" }).click();
  await expect(page.locator("html")).toHaveAttribute("lang", "hi-IN");
  await page.getByRole("button", { name: /रवि का काल्पनिक केस खोलें/i }).click();
  await page.getByRole("button", { name: /क्लेम प्री-फ्लाइट चलाएँ/i }).click();
  await page.getByRole("button", { name: /न्यूनतम सुधार का डेमो/i }).click();
  await expect(page.getByText(/डेमो जाँच पास/i)).toBeVisible();
  await expect(page.locator("body")).not.toContainText(/claimpath\.[a-z0-9_.]+/i);
});

test("320px mobile keeps the complete journey without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 });
  await page.reload();
  await diagnose(page);
  await page.getByRole("button", { name: /simulate minimum fix/i }).click();
  expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(1);
  await page.screenshot({ path: "../../output/screenshots/claimpath-mobile-320.png", fullPage: true });
});

test("sources and privacy remain available as supporting routes", async ({ page }) => {
  for (const route of ["/sources", "/privacy"]) {
    await page.goto(route);
    await expect(page.locator("h1")).toHaveCount(1);
    await expect(page.getByText(/fictional demo.+not epfo/i)).toBeVisible();
    const accessibility = await new AxeBuilder({ page }).analyze();
    expect(accessibility.violations.filter((item) => item.impact === "serious" || item.impact === "critical")).toEqual([]);
  }
});
