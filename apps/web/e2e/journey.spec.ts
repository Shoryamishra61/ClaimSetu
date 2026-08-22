import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function startCase(page: Page, heading: RegExp) {
  const card = page
    .getByRole("article")
    .filter({ has: page.getByRole("heading", { name: heading }) });
  await card.getByRole("button", { name: /try this case/i }).click();
}

async function chooseRoute(page: Page, heading: RegExp) {
  const option = page
    .getByRole("article")
    .filter({ has: page.getByRole("heading", { name: heading }) });
  await option.getByRole("button", { name: /simulate this route/i }).click();
  await expect(
    page.getByRole("dialog", { name: /simulate this correction/i }),
  ).toBeVisible();
  await page.getByRole("button", { name: /simulate correction/i }).click();
}

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => sessionStorage.clear());
  await page.reload();
});

test("prototype disclosure, keyboard skip link, and serious accessibility gate", async ({
  page,
}) => {
  await expect(
    page.getByText(/independent hackathon prototype/i).first(),
  ).toBeVisible();
  await expect(page.getByText(/do not enter real aadhaar/i)).toBeVisible();
  await expect(
    page.getByRole("button", { name: /try this case/i }),
  ).toHaveCount(3);
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: /skip to main content/i }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main")).toBeFocused();

  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(
    accessibility.violations.filter(
      (item) => item.impact === "serious" || item.impact === "critical",
    ),
  ).toEqual([]);
});

test("Scenario A recommends the narrow correction and reaches a reversible ready state", async ({
  page,
}) => {
  await startCase(page, /can't fetch my driving licence/i);
  await expect(page.getByText("Blocked", { exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByText("Blocked", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("heading", {
      name: /name representations do not reconcile/i,
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await expect(page.getByText(/recommended in this simulation/i)).toBeVisible();
  const recommended = page
    .getByRole("article")
    .filter({
      has: page.getByRole("heading", {
        name: /align the fictional dl source name/i,
      }),
    })
    .getByRole("button", { name: /simulate this route/i });
  await recommended.focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("dialog", { name: /simulate this correction/i }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(recommended).toBeFocused();
  await page.keyboard.press("Enter");
  await page.getByRole("button", { name: /simulate correction/i }).click();
  await expect(page.locator(".status-label")).toContainText(
    /ready in this simulation/i,
  );
  await expect(page.getByText(/no official record was changed/i)).toBeVisible();
  await expect(page.locator(".before-after")).toContainText(
    "KRISHNAN ANANYA RAMESH",
  );
  await expect(page.locator(".before-after")).toContainText(
    "ANANYA RAMESH KRISHNAN",
  );
  await page.getByRole("button", { name: /undo last simulation/i }).click();
  await expect(page.getByText("Blocked", { exact: true })).toBeVisible();
});

test("Scenario B proves the visible name difference is not causal", async ({
  page,
}) => {
  await startCase(page, /pf\/kyc issue/i);
  await expect(page.locator(".status-label")).toContainText(
    /not an identity-data issue/i,
  );
  await expect(
    page.getByRole("heading", {
      name: /service-history date blocks this task/i,
    }),
  ).toBeVisible();

  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await chooseRoute(page, /align the fictional pan display name/i);
  await expect(page.locator(".status-label")).toContainText(
    /not an identity-data issue/i,
  );
  await expect(
    page.getByRole("heading", {
      name: /service-history date blocks this task/i,
    }),
  ).toBeVisible();

  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await chooseRoute(page, /correct the fictional service-history date/i);
  await expect(page.locator(".status-label")).toContainText(
    /ready in this simulation/i,
  );
  await expect(
    page.getByText(/service-history condition now passes/i),
  ).toBeVisible();
});

test("Scenario C resolves only the selected goal and preserves non-blocking differences", async ({
  page,
}) => {
  await startCase(page, /name or address changed/i);
  await expect(
    page.getByRole("heading", {
      name: /one targeted name correction is enough/i,
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await chooseRoute(
    page,
    /use the chosen current name in the fictional dl source/i,
  );
  await expect(page.locator(".status-label")).toContainText(
    /ready in this simulation/i,
  );
  await expect(
    page.getByRole("heading", { name: /still different, but not blocking/i }),
  ).toBeVisible();
  await expect(
    page.getByText(/pan demo still uses the earlier name/i),
  ).toBeVisible();
  await expect(page.getByText(/dl address also differs/i)).toBeVisible();
});

test("Hindi journey contains no leaked translation keys", async ({ page }) => {
  await page.getByRole("button", { name: "हिन्दी" }).click();
  await expect(
    page.getByRole("heading", { name: /जब रिकॉर्ड अलग हों/i }),
  ).toBeVisible();
  const firstCard = page.getByRole("article").first();
  await firstCard.getByRole("button", { name: /यह केस आज़माएँ/i }).click();
  await expect(page.getByText("रुका हुआ", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: /सुधार के विकल्प देखें/i })
    .click();
  const recommended = page
    .getByRole("article")
    .filter({ hasText: "इस डेमो में सुझाया गया" });
  await recommended
    .getByRole("button", { name: /इस विकल्प को डेमो में आज़माएँ/i })
    .click();
  await page
    .getByRole("button", { name: /सुधार का डेमो करें/i })
    .click();
  await expect(page.locator(".status-label")).toContainText(
    /इस डेमो में तैयार/i,
  );
  await expect(
    page.getByRole("link", { name: /आधिकारिक स्रोत खोलें/i }),
  ).toBeVisible();
  await expect(page.locator("body")).not.toContainText(
    /(?:diagnosis|finding|scenario|action|handoff)\.[a-z0-9_.]+/i,
  );
});

test("320px mobile and 200 percent zoom retain the critical flow without overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 800 });
  await page.reload();
  await expect(
    page.getByRole("heading", { name: /when records disagree/i }),
  ).toBeVisible();
  await startCase(page, /can't fetch my driving licence/i);
  await expect(page.getByText("Blocked", { exact: true })).toBeVisible();
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth -
        document.documentElement.clientWidth,
    ),
  ).toBeLessThanOrEqual(1);
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await chooseRoute(page, /align the fictional dl source name/i);
  await expect(page.locator(".status-label")).toContainText(
    /ready in this simulation/i,
  );
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth -
        document.documentElement.clientWidth,
    ),
  ).toBeLessThanOrEqual(1);
  await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur());
  await page.addStyleTag({ content: ".skip-link { display: none !important; }" });
  await page.screenshot({
    path: "../../output/screenshots/identity-rescue-mobile-320.png",
    fullPage: true,
  });

  await page.setViewportSize({ width: 1280, height: 900 });
  await page.evaluate(() => sessionStorage.clear());
  await page.goto("/");
  await page.reload();
  await page.evaluate(() => {
    document.documentElement.style.zoom = "2";
  });
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth -
        document.documentElement.clientWidth,
    ),
  ).toBeLessThanOrEqual(1);
  await page.screenshot({
    path: "../../output/screenshots/identity-rescue-desktop-200pct.png",
    fullPage: true,
  });
});
