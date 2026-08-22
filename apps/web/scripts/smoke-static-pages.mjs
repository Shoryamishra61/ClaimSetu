import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { extname, join, normalize, resolve } from "node:path";

import { chromium } from "playwright";

const root = resolve("dist-pages");
const prefix = "/handover29c";
const port = 8132;
const remoteBaseUrl = process.env.STATIC_BASE_URL?.replace(/\/$/, "");
const mime = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".map": "application/json; charset=utf-8",
};

const server = createServer(async (request, response) => {
  const requestPath = decodeURIComponent(new URL(request.url ?? "/", "http://local").pathname);
  if (!requestPath.startsWith(prefix)) {
    response.writeHead(404).end();
    return;
  }
  const relative = normalize(requestPath.slice(prefix.length) || "/")
    .replace(/^[/\\]+/, "")
    .replace(/^(\.\.[/\\])+/, "");
  let target = join(root, relative || "index.html");
  try {
    if ((await stat(target)).isDirectory()) target = join(target, "index.html");
    const body = await readFile(target);
    response.writeHead(200, { "Content-Type": mime[extname(target)] ?? "application/octet-stream" });
    response.end(body);
  } catch {
    const isClientRoute = !extname(relative);
    const body = isClientRoute ? await readFile(join(root, "404.html")) : Buffer.from("");
    response.writeHead(404, {
      "Content-Type": isClientRoute ? mime[".html"] : "text/plain; charset=utf-8",
    });
    response.end(body);
  }
});

function startCase(page, heading) {
  return page
    .getByRole("article")
    .filter({ has: page.getByRole("heading", { name: heading }) })
    .getByRole("button", { name: /try this case/i })
    .click();
}

async function simulate(page, heading) {
  const option = page
    .getByRole("article")
    .filter({ has: page.getByRole("heading", { name: heading }) });
  await option.getByRole("button", { name: /simulate this route/i }).click();
  await page.getByRole("button", { name: /simulate correction/i }).click();
}

if (!remoteBaseUrl) {
  await new Promise((ready) => server.listen(port, "127.0.0.1", ready));
}
let browser;
try {
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const externalRequests = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    const allowedHost = remoteBaseUrl ? new URL(remoteBaseUrl).hostname : "127.0.0.1";
    if (url.hostname !== allowedHost) externalRequests.push(url.href);
  });
  await page.goto(remoteBaseUrl ? `${remoteBaseUrl}/` : `http://127.0.0.1:${port}${prefix}/`);

  await startCase(page, /can't fetch my driving licence/i);
  await page.getByText("Blocked", { exact: true }).last().waitFor();
  await page.reload();
  await page.getByText("Blocked", { exact: true }).last().waitFor();
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await simulate(page, /align the fictional dl source name/i);
  await page.getByText(/ready in this simulation/i).last().waitFor();

  await page.getByRole("button", { name: /identity rescue: all demo cases/i }).click();
  await startCase(page, /pf\/kyc issue/i);
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await simulate(page, /align the fictional pan display name/i);
  await page.getByText(/not an identity-data issue/i).last().waitFor();
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await simulate(page, /correct the fictional service-history date/i);
  await page.getByText(/ready in this simulation/i).last().waitFor();

  await page.getByRole("button", { name: /identity rescue: all demo cases/i }).click();
  await startCase(page, /name or address changed/i);
  await page.getByRole("button", { name: /compare ways to fix this/i }).click();
  await simulate(page, /use the chosen current name in the fictional dl source/i);
  await page.getByRole("heading", { name: /still different, but not blocking/i }).waitFor();

  await page.getByRole("button", { name: /identity rescue: all demo cases/i }).click();
  await page.getByRole("button", { name: /sources & limits/i }).first().click();
  const officialLinks = await page.locator('main a[target="_blank"]').evaluateAll((links) =>
    links.map((link) => ({
      href: link.getAttribute("href"),
      rel: link.getAttribute("rel"),
    })),
  );
  const expectedSources = new Set([
    "https://www.digilocker.gov.in/web/about/faq",
    "https://uidai.gov.in/images/LR_Aadhaar_Handbook_2026.pdf",
    "https://www.epfindia.gov.in/site_docs/PDFs/Circulars/Y2020-2021/FAQUANKYC.pdf",
  ]);
  if (
    officialLinks.length !== expectedSources.size ||
    officialLinks.some(
      (link) =>
        !expectedSources.has(link.href) ||
        link.rel !== "noopener noreferrer",
    )
  ) {
    throw new Error(`Static source allowlist drift: ${JSON.stringify(officialLinks)}`);
  }

  if (externalRequests.length) {
    throw new Error(`Static demo made unexpected external requests: ${externalRequests.join(", ")}`);
  }
  process.stdout.write("STATIC_PAGES_GOLDEN_PATHS=PASS\n");
} finally {
  if (browser) await browser.close();
  if (!remoteBaseUrl) {
    await new Promise((closed) => server.close(closed));
  }
}
