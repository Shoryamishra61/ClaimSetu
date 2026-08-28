import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { extname, join, normalize, resolve } from "node:path";
import { chromium } from "playwright";

const root = resolve("dist-pages");
const prefix = "/ClaimSetu";
const port = 8132;
const remoteBaseUrl = process.env.STATIC_BASE_URL?.replace(/\/$/, "");
const mime = { ".css": "text/css; charset=utf-8", ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8" };

const server = createServer(async (request, response) => {
  const requestPath = decodeURIComponent(new URL(request.url ?? "/", "http://local").pathname);
  if (!requestPath.startsWith(prefix)) return response.writeHead(404).end();
  const relative = normalize(requestPath.slice(prefix.length) || "/").replace(/^[/\\]+/, "").replace(/^(\.\.[/\\])+/, "");
  let target = join(root, relative || "index.html");
  try {
    if ((await stat(target)).isDirectory()) target = join(target, "index.html");
    response.writeHead(200, { "Content-Type": mime[extname(target)] ?? "application/octet-stream" });
    response.end(await readFile(target));
  } catch {
    const isClientRoute = !extname(relative);
    response.writeHead(404, { "Content-Type": isClientRoute ? mime[".html"] : "text/plain; charset=utf-8" });
    response.end(isClientRoute ? await readFile(join(root, "404.html")) : Buffer.from(""));
  }
});

if (!remoteBaseUrl) await new Promise((ready) => server.listen(port, "127.0.0.1", ready));
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
  await page.getByRole("button", { name: /find what blocks the transfer/i }).click();
  await page.getByText(/blocked in this model/i).waitFor();
  await page.getByRole("button", { name: /simulate minimum fix/i }).click();
  await page.getByText(/modeled checks pass/i).first().waitFor();
  const official = await page.getByRole("link", { name: /open epfo member portal/i }).getAttribute("href");
  if (!official?.startsWith("https://unifiedportal-mem.epfindia.gov.in/")) throw new Error(`Official handoff drift: ${official}`);
  const fallback = await page.getByRole("link", { name: /use official umang epfo services/i }).getAttribute("href");
  if (!fallback?.startsWith("https://web.umang.gov.in/")) throw new Error(`UMANG fallback drift: ${fallback}`);
  const rootUrl = remoteBaseUrl ? `${remoteBaseUrl}/test-case/` : `http://127.0.0.1:${port}${prefix}/test-case/`;
  await page.goto(rootUrl);
  await page.getByRole("button", { name: /load sample now/i }).click();
  await page.getByText("claimpath-epfo-test-case.json").waitFor();
  await page.getByRole("button", { name: /run deterministic check/i }).click();
  await page.getByRole("heading", { name: /date of exit blocks this sample/i }).waitFor();
  await page.getByText(/browser fallback/i).waitFor();
  await page.getByRole("button", { name: /test proposed date of exit/i }).click();
  await page.getByRole("heading", { name: /transfer prerequisite is met/i }).waitFor();
  if (externalRequests.length) throw new Error(`Static demo made unexpected external requests: ${externalRequests.join(", ")}`);
  process.stdout.write("STATIC_PAGES_CLAIMSETU_JOURNEY_AND_TEST_HARNESS=PASS\n");
} finally {
  if (browser) await browser.close();
  if (!remoteBaseUrl) await new Promise((closed) => server.close(closed));
}
