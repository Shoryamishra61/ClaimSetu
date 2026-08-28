import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "playwright";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(scriptDir, "../../..");
const videoPath = join(
  projectRoot,
  "output",
  "video",
  "claimsetu-final-submission.mp4",
);
const body = await readFile(videoPath);
const port = 8136;
const server = createServer((request, response) => {
  if (request.url === "/") {
    const html = Buffer.from(
      '<!doctype html><style>*{box-sizing:border-box}html,body{margin:0;background:#111}video{display:block;width:1280px;height:720px}</style><video id="demo" muted preload="auto" src="/demo.mp4"></video>',
    );
    response.writeHead(200, {
      "Content-Type": "text/html; charset=utf-8",
      "Content-Length": html.length,
    });
    response.end(html);
    return;
  }
  if (request.url === "/demo.mp4") {
    response.writeHead(200, {
      "Content-Type": "video/mp4",
      "Content-Length": body.length,
    });
    response.end(body);
    return;
  }
  response.writeHead(404).end();
});

await new Promise((ready) => server.listen(port, "127.0.0.1", ready));
let browser;
try {
  browser = await chromium.launch({
    headless: true,
    args: ["--autoplay-policy=no-user-gesture-required"],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.goto(`http://127.0.0.1:${port}/`);
  const metadata = await page.locator("#demo").evaluate(async (element) => {
    if (!(element instanceof HTMLVideoElement)) throw new Error("Video unavailable");
    if (element.readyState < HTMLMediaElement.HAVE_METADATA) {
      await new Promise((resolveReady) =>
        element.addEventListener("loadedmetadata", resolveReady, { once: true }),
      );
    }
    await element.play();
    await new Promise((resolveWait) => setTimeout(resolveWait, 250));
    const stream = element.captureStream();
    element.pause();
    return {
      duration: element.duration,
      width: element.videoWidth,
      height: element.videoHeight,
      audioTracks: stream.getAudioTracks().length,
      videoTracks: stream.getVideoTracks().length,
    };
  });
  if (
    metadata.duration < 110 ||
    metadata.duration > 120 ||
    metadata.width !== 1280 ||
    metadata.height !== 720 ||
    metadata.audioTracks !== 1 ||
    metadata.videoTracks !== 1
  ) {
    throw new Error(`Final demo media gate failed: ${JSON.stringify(metadata)}`);
  }
  process.stdout.write(
    `FINAL_VIDEO_SECONDS=${metadata.duration.toFixed(3)} DIMENSIONS=${metadata.width}x${metadata.height} AUDIO_TRACKS=${metadata.audioTracks} VIDEO_TRACKS=${metadata.videoTracks}\n`,
  );
} finally {
  if (browser) await browser.close();
  await new Promise((closed) => server.close(closed));
}
