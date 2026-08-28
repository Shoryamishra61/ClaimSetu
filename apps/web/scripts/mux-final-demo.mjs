import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "playwright";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(scriptDir, "../../..");
const outputDir = join(projectRoot, "output", "video");
const visualPath = join(outputDir, "claimsetu-final-visual.webm");
const narrationPaths = Array.from({ length: 10 }, (_, index) =>
  join(outputDir, `claimsetu-narration-${String(index + 1).padStart(2, "0")}.wav`),
);
const destination = join(outputDir, "claimsetu-final-submission.webm");
const port = 8135;

const server = createServer(async (request, response) => {
  if (request.url === "/") {
    const body = Buffer.from(
      '<!doctype html><video id="visual" muted preload="auto" src="/visual"></video>',
    );
    response.writeHead(200, {
      "Content-Type": "text/html; charset=utf-8",
      "Content-Length": body.length,
    });
    response.end(body);
    return;
  }
  const audioMatch = /^\/audio\/(\d+)$/.exec(request.url ?? "");
  const path =
    request.url === "/visual"
      ? visualPath
      : audioMatch
        ? narrationPaths[Number(audioMatch[1])]
        : null;
  if (!path) {
    response.writeHead(404).end();
    return;
  }
  const body = await readFile(path);
  response.writeHead(200, {
    "Content-Type": request.url === "/visual" ? "video/webm" : "audio/wav",
    "Content-Length": body.length,
    "Accept-Ranges": "bytes",
    "Access-Control-Allow-Origin": "*",
  });
  response.end(body);
});

await new Promise((ready) => server.listen(port, "127.0.0.1", ready));
let browser;
try {
  browser = await chromium.launch({
    headless: true,
    args: ["--autoplay-policy=no-user-gesture-required"],
  });
  const page = await browser.newPage({ acceptDownloads: true });
  await page.goto(`http://127.0.0.1:${port}/`);
  const downloadPromise = page.waitForEvent("download", { timeout: 150_000 });
  let encodingEvidence;
  try {
    encodingEvidence = await page.evaluate(async ({ port: mediaPort }) => {
    const visual = document.querySelector("#visual");
    if (!(visual instanceof HTMLVideoElement)) {
      throw new Error("Demo media elements unavailable");
    }
    if (visual.readyState < HTMLMediaElement.HAVE_ENOUGH_DATA) {
      await new Promise((resolve) =>
        visual.addEventListener("canplaythrough", resolve, { once: true }),
      );
    }
    const audioContext = new AudioContext();
    const audioDestination = audioContext.createMediaStreamDestination();
    const buffers = await Promise.all(
      Array.from({ length: 10 }, async (_, index) => {
        const response = await fetch(`http://127.0.0.1:${mediaPort}/audio/${index}`);
        return audioContext.decodeAudioData(await response.arrayBuffer());
      }),
    );
    const starts = [0, 8, 23, 35, 48, 60, 72, 85, 98, 108];
    const ends = [8, 23, 35, 48, 60, 72, 85, 98, 108, 116];
    buffers.forEach((buffer, index) => {
      if (buffer.duration > ends[index] - starts[index]) {
        throw new Error(
          `Narration segment ${index + 1} is ${buffer.duration.toFixed(2)}s but its slot is ${ends[index] - starts[index]}s`,
        );
      }
    });
    const visualStream = visual.captureStream();
    const combined = new MediaStream([
      ...visualStream.getVideoTracks(),
      ...audioDestination.stream.getAudioTracks(),
    ]);
    const chunks = [];
    const recorder = new MediaRecorder(combined, {
      mimeType: "video/webm;codecs=vp9,opus",
      videoBitsPerSecond: 4_000_000,
      audioBitsPerSecond: 128_000,
    });
    recorder.addEventListener("dataavailable", (event) => {
      if (event.data.size) chunks.push(event.data);
    });
    const stopped = new Promise((resolve) => recorder.addEventListener("stop", resolve, { once: true }));
    const recordingStarted = performance.now();
    recorder.start(1_000);
    await audioContext.resume();
    const audioStart = audioContext.currentTime + 0.1;
    buffers.forEach((buffer, index) => {
      const source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(audioDestination);
      source.start(audioStart + starts[index]);
    });
    await visual.play();
    await new Promise((resolve) => visual.addEventListener("ended", resolve, { once: true }));
    recorder.stop();
    await stopped;
    const blob = new Blob(chunks, { type: "video/webm" });
    const anchor = document.createElement("a");
    anchor.href = URL.createObjectURL(blob);
    anchor.download = "claimsetu-final-submission.webm";
    anchor.click();
    return {
      segmentDurations: buffers.map((buffer) => Number(buffer.duration.toFixed(3))),
      durationMs: performance.now() - recordingStarted,
    };
    }, { port });
  } catch (error) {
    void downloadPromise.catch(() => undefined);
    throw error;
  }
  const download = await downloadPromise;
  await download.saveAs(destination);
  process.stdout.write(
    `NARRATION_SEGMENT_SECONDS=${encodingEvidence.segmentDurations.join(",")} ENCODED_DURATION_MS=${encodingEvidence.durationMs.toFixed(0)}\n`,
  );
  process.stdout.write(`FINAL_SUBMISSION_VIDEO=${destination}\n`);
} finally {
  if (browser) await browser.close();
  await new Promise((closed) => server.close(closed));
}
