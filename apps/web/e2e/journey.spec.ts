import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function loadRavi(page: Page) {
  await page.getByRole("button", { name: /find what blocks the transfer/i }).click();
  await expect(page.getByText(/blocked in this model/i)).toBeVisible();
}

async function diagnose(page: Page) {
  await loadRavi(page);
}

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => sessionStorage.clear());
  await page.reload();
});

test("focused entry is safe, keyboard reachable, and accessible", async ({ page }) => {
  await expect(page).toHaveTitle(/ClaimPath/);
  await expect(page.getByRole("heading", { name: /ravi cannot move his old pf balance/i })).toBeVisible();
  await expect(page.getByText(/independent prototype.+fictional data.+no government connection/i).first()).toBeVisible();
  await expect(page.getByText(/no uan, aadhaar, pan, otp/i)).toBeVisible();
  await expect(page.getByText(/previous pf account not available to transfer/i)).toBeVisible();
  await expect(page.getByRole("textbox")).toHaveCount(0);
  await page.screenshot({ path: "../../output/audit-final/01-entry.png", fullPage: true });
  await expect(page.locator('meta[http-equiv="Content-Security-Policy"]')).toHaveAttribute("content", /object-src 'none'/);
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: /skip to main content/i })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main")).toBeFocused();
  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(accessibility.violations.filter((item) => item.impact === "serious" || item.impact === "critical")).toEqual([]);
});

test("two-action journey finds the causal blocker and proves the minimum fix", async ({ page }) => {
  await loadRavi(page);
  await expect(page.getByText(/ravi k/i).first()).toBeVisible();
  await expect(page.getByText(/blocked in this model/i)).toBeVisible();
  await expect(page.getByRole("heading", { name: /date of exit is missing/i })).toBeVisible();
  await expect(page.getByText(/do not change the name for this blocker/i)).toBeVisible();
  await page.screenshot({ path: "../../output/audit-final/02-diagnosis.png", fullPage: true });
  await page.getByText(/view technical evidence/i).click();
  await expect(page.getByText(/epfo documents this prerequisite/i)).toBeVisible();
  await expect(page.getByRole("link", { name: /epfo faq.+employees/i })).toHaveAttribute("href", /epfindia\.gov\.in\/site_en\/FAQ\.php/);
  await page.getByRole("button", { name: /simulate minimum fix/i }).click();
  await expect(page.getByText(/modeled checks pass/i).first()).toBeVisible();
  await expect(page.getByText(/does not submit or approve a real transfer/i)).toBeVisible();
  await page.screenshot({ path: "../../output/audit-final/03-result.png", fullPage: true });
  const official = page.getByRole("link", { name: /open epfo member portal/i });
  await expect(official).toHaveAttribute("href", /unifiedportal-mem\.epfindia\.gov\.in/);
  await expect(official).toHaveAttribute("rel", "noopener noreferrer");
  await expect(page.getByRole("link", { name: /use official umang epfo services/i })).toHaveAttribute("href", /web\.umang\.gov\.in/);
});

test("Hindi journey has no leaked translation keys", async ({ page }) => {
  await page.getByRole("button", { name: "हिन्दी" }).click();
  await expect(page.locator("html")).toHaveAttribute("lang", "hi-IN");
  await page.getByRole("button", { name: /ट्रांसफर की रुकावट खोजें/i }).click();
  await page.getByRole("button", { name: /न्यूनतम सुधार का डेमो/i }).click();
  await expect(page.getByText(/डेमो जाँच पास/i).first()).toBeVisible();
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
    await expect(page.getByText(/independent prototype.+fictional data.+no government connection/i).first()).toBeVisible();
    const accessibility = await new AxeBuilder({ page }).analyze();
    expect(accessibility.violations.filter((item) => item.impact === "serious" || item.impact === "critical")).toEqual([]);
  }
});
