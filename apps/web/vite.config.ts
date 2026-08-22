/// <reference types="vitest" />
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// The API owns the disclosure copy, the policy text and the poll interval, so the
// dev server proxies rather than duplicating a base URL in the client: the SPA
// always talks to a same-origin `/api`, in development and in the deployed
// single-container build alike. One code path, so "it worked on localhost" cannot
// mean something different from "it worked on the deployed URL".
const API_TARGET = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": { target: API_TARGET, changeOrigin: true },
      "/healthz": { target: API_TARGET, changeOrigin: true },
      "/ws": { target: API_TARGET, ws: true, changeOrigin: true },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
    // No dynamic chunking games. A single bundle keeps the CSP simple
    // (`script-src 'self'`, no inline) and makes the deployed artefact easy to
    // reason about.
    chunkSizeWarningLimit: 900,
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    include: ["tests/**/*.test.{ts,tsx}"],
    css: false,
  },
});
