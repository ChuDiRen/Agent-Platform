import { test as setup, expect } from "@playwright/test";

const authFile = ".auth/user.json";

setup("authenticate", async ({ page }) => {
  // Mock the login API to return a successful response
  await page.route("**/api/v1/users/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "mock-jwt-token-for-testing",
        token_type: "bearer",
        user: {
          id: 1,
          email: "test@example.com",
          full_name: "测试用户",
          is_superuser: true,
        },
      }),
    });
  });

  await page.goto("/login");
  await page.getByPlaceholder("邮箱地址").fill("test@example.com");
  await page.getByPlaceholder("密码").fill("Test123456");
  await page.getByRole("button", { name: "登录" }).click();

  // Wait for navigation to home
  await page.waitForURL("/home");

  // Save storage state (cookies + localStorage)
  await page.context().storageState({ path: authFile });
});
