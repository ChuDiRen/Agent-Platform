import { test as setup, expect } from "@playwright/test";
import { registerUser, loginUser } from "./helpers";

const authFile = ".auth/user.json";
const EMAIL = "e2e_admin@test.com";
const PASSWORD = "E2eTest123!";

setup("authenticate via real backend", async ({ page, request }) => {
  // Register (idempotent — 200 or 400 both fine)
  await registerUser(request, EMAIL, PASSWORD, "E2E管理员");

  // Login and get real token
  const token = await loginUser(request, EMAIL, PASSWORD);

  // Set token in localStorage before navigating
  await page.addInitScript(
    ({ token, email }) => {
      localStorage.setItem(
        "user_info",
        JSON.stringify({
          state: {
            token,
            userName: "E2E管理员",
            avatar: "",
            role: "admin",
          },
        }),
      );
    },
    { token, email: EMAIL },
  );

  // Navigate to trigger cookie/token setup
  await page.goto("/projects");
  await expect(page.getByText("项目管理")).toBeVisible();

  // Save storage state
  await page.context().storageState({ path: authFile });
});
