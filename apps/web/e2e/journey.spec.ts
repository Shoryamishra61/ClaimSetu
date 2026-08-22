import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => sessionStorage.clear());
  await page.reload();
});

test("keyboard route entry, disclosure, and accessibility", async ({ page }) => {
  await expect(page.getByText(/simulated government integrations/i).first()).toBeVisible();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: /skip to main content/i })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();

  const accessibility = await new AxeBuilder({ page }).analyze();
  const severe = accessibility.violations.filter((item) =>
    item.impact === "serious" || item.impact === "critical",
  );
  expect(severe).toEqual([]);
});

test("real four-state journey downloads an extractable prototype PDF", async ({ page }) => {
  await page.getByRole("button", { name: /handing it to an authorised dealer/i }).click();
  await page.getByRole("button", { name: /use demo vehicle/i }).click();
  await page.getByRole("button", { name: /verify and continue/i }).click();
  await expect(page.getByText("INITIATED", { exact: true })).toBeVisible();

  await page.getByRole("button", { name: /use demo dealer/i }).click();
  await page.getByRole("button", { name: /verify dealer/i }).click();
  await expect(page.getByText("DEALER_SELECTED", { exact: true })).toBeVisible();

  await page.getByLabel(/odometer reading/i).fill("12345");
  await page.getByRole("checkbox").nth(0).check();
  await page.getByRole("checkbox").nth(1).check();
  await page.getByRole("button", { name: /confirm handover/i }).click();
  await expect(page.getByText("CUSTODY_TRANSFERRED", { exact: true })).toBeVisible();
  await expect(page.getByText(/not a portal acknowledgement/i)).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("link", { name: /download prototype form 29c pdf/i }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^handover29c-case-.+\.pdf$/);
});

test("320px and 200 percent zoom retain the critical flow without overflow", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 });
  await page.reload();
  await expect(page.getByRole("heading", { name: /vehicle handover to a dealer/i })).toBeVisible();
  const mobileOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(mobileOverflow).toBeLessThanOrEqual(1);
  await page.screenshot({ path: "../../output/screenshots/handover29c-mobile-320.png", fullPage: true });

  await page.setViewportSize({ width: 1280, height: 900 });
  await page.reload();
  await page.evaluate(() => { document.documentElement.style.zoom = "2"; });
  const zoomOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(zoomOverflow).toBeLessThanOrEqual(1);
  await page.screenshot({ path: "../../output/screenshots/handover29c-desktop-200pct.png", fullPage: true });
});
