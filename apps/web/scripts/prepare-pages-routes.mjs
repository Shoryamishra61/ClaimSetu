import { copyFile, mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const output = resolve("dist-pages");
const index = resolve(output, "index.html");

await copyFile(index, resolve(output, "404.html"));
await writeFile(resolve(output, ".nojekyll"), "");
for (const route of ["test-case", "sources", "privacy"]) {
  const directory = resolve(output, route);
  await mkdir(directory, { recursive: true });
  await copyFile(index, resolve(directory, "index.html"));
}

process.stdout.write("PAGES_CLIENT_ROUTES=READY\n");
