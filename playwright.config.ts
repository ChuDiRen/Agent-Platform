import { defineConfig, devices } from "@playwright/test";

const localChromium =
  process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ||
  "C:\\Users\\Administrator\\AppData\\Local\\ms-playwright\\chromium-1208\\chrome-win\\chrome.exe";

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: "**/*.spec.ts",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [["html"], ["list"]],

  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "on-first-retry",
  },

  projects: [
    {
      name: "setup",
      testMatch: /.*\.setup\.ts/,
      use: { launchOptions: { executablePath: localChromium } },
    },
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        storageState: ".auth/user.json",
        launchOptions: { executablePath: localChromium },
      },
      dependencies: ["setup"],
    },
  ],

  webServer: [
    {
      command: "cd backend && .\\venv\\Scripts\\uvicorn app.main:app --port 8000",
      url: "http://localhost:8000/health",
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
    {
      command: "cd fronted && pnpm dev",
      url: "http://localhost:3000",
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
  ],
});
