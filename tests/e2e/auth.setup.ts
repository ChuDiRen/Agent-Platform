import { test as setup, expect } from "@playwright/test";
import { registerUser, loginUser } from "./helpers";

const authFile = ".auth/user.json";
const EMAIL = `e2e_admin_${Date.now()}@test.com`;
const PASSWORD = "E2eTest123!";

setup("authenticate via real backend", async ({ page, request }) => {
  // Register (idempotent — 200 or 400 both fine)
  await registerUser(request, EMAIL, PASSWORD, "E2E管理员");

  // Login and get real token
  const token = await loginUser(request, EMAIL, PASSWORD);

  // Save real token in both places used by the app: Cookie for guards/API and localStorage for UI state.
  await page.context().addCookies([
    {
      name: "vue3_token",
      value: token,
      domain: "localhost",
      path: "/",
    },
  ]);

  await page.addInitScript(
    ({ token }) => {
      localStorage.setItem(
        "user_info",
        JSON.stringify({
          token,
          userName: "E2E管理员",
          avatar: "",
          role: "admin",
        }),
      );
    },
    { token },
  );

  // Navigate to trigger cookie/token setup
  await page.goto("/projects");
  await expect(page.getByText("项目管理")).toBeVisible();

  // Save storage state
  await page.context().storageState({ path: authFile });
});
