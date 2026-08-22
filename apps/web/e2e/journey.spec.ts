import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function startCase(page: Page, scenarioId: string) {
  await page.getByLabel(/service goal/i).selectOption(scenarioId);
  await page.getByRole("button", { name: /run pre-flight diagnosis/i }).click();
}

async function chooseRoute(page: Page, heading: RegExp) {
  const option = page
    .getByRole("article")
    .filter({ has: page.getByRole("heading", { name: heading }) });
  const trigger = option.getByRole("button", { name: /simulate this route/i });
  await trigger.focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("dialog", { name: /simulate this correction/i }),
  ).toBeVisible();
  const confirm = page.getByRole("button", { name: /simulate correction/i });
  await confirm.focus();
  await page.keyboard.press("Enter");
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
  await expect(page.getByLabel(/service goal/i)).toBeVisible();
  await expect(page.getByLabel(/describe what happened/i)).toBeEditable();
  await expect(page.getByRole("button", { name: /run pre-flight diagnosis/i })).toBeVisible();
  await expect(
    page.locator('meta[http-equiv="Content-Security-Policy"]'),
  ).toHaveAttribute("content", /object-src 'none'/);
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

test("every public route has one H1, disclosure, locale metadata, and no serious accessibility violation", async ({
  page,
}) => {
  const routes = [
    "/",
    "/sources",
    "/privacy",
    "/case/digilocker-dl",
    "/case/epfo-preflight",
    "/case/life-event",
  ];
  for (const route of routes) {
    await page.goto(route);
    await expect(page.locator("h1")).toHaveCount(1);
    await expect(page.locator("h1")).not.toBeEmpty();
    await expect(
      page.getByText(/independent hackathon prototype/i).first(),
    ).toBeVisible();
    await expect(page.locator("html")).toHaveAttribute("lang", "en-IN");
    await expect(page).toHaveTitle(/Identity Rescue/);
    const accessibility = await new AxeBuilder({ page }).analyze();
    expect(
      accessibility.violations.filter(
        (item) => item.impact === "serious" || item.impact === "critical",
      ),
      `serious/critical accessibility violation on ${route}`,
    ).toEqual([]);
  }
});

test("Scenario A recommends the narrow correction and reaches a reversible ready state", async ({
  page,
}) => {
  await startCase(page, "digilocker-dl");
  await expect(page.locator(".route-announcement")).toContainText(
    /can't fetch my driving licence/i,
  );
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
  await startCase(page, "epfo-preflight");
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
  await startCase(page, "life-event");
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

test("reset clears mutations and browser back-forward restores only deterministic state", async ({
  page,
}) => {
  await startCase(page, "digilocker-dl");
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await chooseRoute(page, /align the fictional dl source name/i);
  await expect(page.locator(".status-label")).toContainText(
    /ready in this simulation/i,
  );

  await page.goBack();
  await expect(
    page.getByRole("heading", { name: /find what is blocking/i }),
  ).toBeVisible();
  await page.goForward();
  await expect(page.locator(".status-label")).toContainText(
    /ready in this simulation/i,
  );

  await page.getByRole("button", { name: /reset demo/i }).first().click();
  await expect(
    page.getByRole("heading", { name: /find what is blocking/i }),
  ).toBeVisible();
  await startCase(page, "digilocker-dl");
  await expect(page.getByText("Blocked", { exact: true })).toBeVisible();
});

test("Hindi journey contains no leaked translation keys", async ({ page }) => {
  await page.getByRole("button", { name: "हिन्दी" }).click();
  await expect(
    page.getByRole("heading", { name: /जानें कि आपकी सरकारी सेवा/i }),
  ).toBeVisible();
  await page.getByRole("button", { name: /प्री-फ्लाइट जाँच चलाएँ/i }).click();
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
    page.getByRole("heading", { name: /find what is blocking/i }),
  ).toBeVisible();
  await startCase(page, "digilocker-dl");
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

test("slow-network entry stays usable and reduced-motion removes transitions", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  const transitionDurationMs = await page.locator("body").evaluate(() => {
    const probe = document.createElement("button");
    probe.className = "primary";
    document.body.append(probe);
    const duration = getComputedStyle(probe).transitionDuration;
    probe.remove();
    return duration.endsWith("ms")
      ? Number.parseFloat(duration)
      : Number.parseFloat(duration) * 1_000;
  });
  expect(transitionDurationMs).toBeLessThanOrEqual(0.01);

  await page.route("**/api/v1/identity/**", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1_200));
    await route.continue();
  });
  const started = Date.now();
  await startCase(page, "digilocker-dl");
  await expect(page.getByText("Blocked", { exact: true })).toBeVisible();
  expect(Date.now() - started).toBeLessThan(20_000);
  await expect(page.getByRole("button", { name: /compare ways/i })).toBeEnabled();
});

test("production shell meets the slow-4G paint targets", async ({ page }) => {
  await page.addInitScript(() => {
    const timing = globalThis as typeof globalThis & {
      __identityRescueLcp?: number;
    };
    new PerformanceObserver((list) => {
      timing.__identityRescueLcp = list.getEntries().at(-1)?.startTime;
    }).observe({ type: "largest-contentful-paint", buffered: true });
  });
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Network.enable");
  await cdp.send("Network.setCacheDisabled", { cacheDisabled: true });
  await cdp.send("Network.emulateNetworkConditions", {
    offline: false,
    latency: 150,
    downloadThroughput: 200_000,
    uploadThroughput: 100_000,
    connectionType: "cellular4g",
  });
  await page.goto("/", { waitUntil: "networkidle" });
  await page.waitForTimeout(500);
  const paint = await page.evaluate(() => {
    const firstContentfulPaint = performance
      .getEntriesByName("first-contentful-paint")
      .at(-1)?.startTime;
    const largestContentfulPaint = (
      globalThis as typeof globalThis & { __identityRescueLcp?: number }
    ).__identityRescueLcp;
    return { firstContentfulPaint, largestContentfulPaint };
  });
  expect(paint.firstContentfulPaint).toBeDefined();
  expect(paint.largestContentfulPaint).toBeDefined();
  expect(paint.firstContentfulPaint!).toBeLessThanOrEqual(2_000);
  expect(paint.largestContentfulPaint!).toBeLessThanOrEqual(2_500);
  process.stdout.write(
    `SLOW4G_FCP_MS=${paint.firstContentfulPaint?.toFixed(0)} SLOW4G_LCP_MS=${paint.largestContentfulPaint?.toFixed(0)}\n`,
  );
  test.info().annotations.push({
    type: "performance",
    description: `slow-4G FCP=${paint.firstContentfulPaint?.toFixed(0)}ms LCP=${paint.largestContentfulPaint?.toFixed(0)}ms`,
  });
});
