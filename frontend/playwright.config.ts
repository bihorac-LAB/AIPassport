import { defineConfig, devices } from '@playwright/test';

/**
 * E2E runs against a real backend and a real PostgreSQL database.
 *
 * Start both first (see README), or let the webServer block build and preview the SPA:
 *   cd backend && .venv/bin/uvicorn app.main:app --port 8000
 *   cd frontend && npm run e2e
 */
const BASE_URL = process.env.E2E_BASE_URL ?? 'http://127.0.0.1:4173';

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['github'], ['list']] : 'list',
  use: {
    baseURL: BASE_URL,
    trace: 'retain-on-failure',
    ...devices['Desktop Chrome'],
  },
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command: 'npm run build:only && npx vite preview --port 4173 --strictPort',
        url: BASE_URL,
        reuseExistingServer: !process.env.CI,
        timeout: 180_000,
      },
});
