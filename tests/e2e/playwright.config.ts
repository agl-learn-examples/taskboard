import { defineConfig, devices } from '@playwright/test';

// Browser tests for the TaskBoard web app, against the RUNNING stack (docker compose up -d --build --wait).
// BASE_URL changes where they point; the default is the gateway on your laptop.
export default defineConfig({
  testDir: '.',
  fullyParallel: true,
  forbidOnly: !!process.env.CI, // a forgotten test.only fails CI instead of skipping every other test
  retries: process.env.CI ? 1 : 0, // locally a failure is a failure; in CI one retry records a trace
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : [['list'], ['html']],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:8080',
    trace: 'on-first-retry', // a trace of the retry: every step, the page, the network
    screenshot: 'only-on-failure',
  },
  projects: [
    // Logs in once and saves the browser's storage, so the login limit (10 a minute) is not used up.
    { name: 'setup', testMatch: /auth\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/priya.json' },
      dependencies: ['setup'],
    },
  ],
});
