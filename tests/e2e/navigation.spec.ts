import { test, expect } from "@playwright/test";

test.describe("路由守卫", () => {
  test("未登录访问首页时重定向到登录页", async ({ page }) => {
    await page.goto("/home");
    await page.waitForURL(/\/login/);
    await expect(page).toHaveURL(/\/login/);
  });

  test("未登录访问登录页时不重定向", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveURL("/login");
    await expect(page.getByText("欢迎回来")).toBeVisible();
  });

  test("未登录访问注册页时不重定向", async ({ page }) => {
    await page.goto("/register");
    await expect(page).toHaveURL("/register");
    await expect(page.getByText("创建账号")).toBeVisible();
  });

  test("根路径重定向到首页", async ({ page }) => {
    await page.goto("/");
    // Without auth, should redirect to login
    await page.waitForURL(/\/login/);
    await expect(page).toHaveURL(/\/login/);
  });

  test("已登录用户访问登录页时重定向到首页", async ({ page }) => {
    // Mock login API
    await page.route("**/api/v1/users/login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "test-token",
          token_type: "bearer",
          user: { id: 1, email: "test@example.com", full_name: "测试", is_superuser: false },
        }),
      });
    });

    // Login first
    await page.goto("/login");
    await page.getByPlaceholder("邮箱地址").fill("test@example.com");
    await page.getByPlaceholder("密码").fill("Test123456");
    await page.getByRole("button", { name: "登录" }).click();
    await page.waitForURL("/home");

    // Try to visit login page again
    await page.goto("/login");
    await page.waitForURL("/home");
    await expect(page).toHaveURL("/home");
  });

  test("登录后跳转到 redirect 参数指定的页面", async ({ page }) => {
    await page.route("**/api/v1/users/login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "test-token",
          token_type: "bearer",
          user: { id: 1, email: "test@example.com", full_name: "测试", is_superuser: false },
        }),
      });
    });

    await page.goto("/login?redirect=/home");
    await page.getByPlaceholder("邮箱地址").fill("test@example.com");
    await page.getByPlaceholder("密码").fill("Test123456");
    await page.getByRole("button", { name: "登录" }).click();

    await page.waitForURL("/home");
    await expect(page).toHaveURL("/home");
  });
});

test.describe("页面间导航", () => {
  test("登录页和注册页可以互相跳转", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("link", { name: "立即注册" }).click();
    await expect(page).toHaveURL("/register");

    await page.getByRole("link", { name: "返回登录" }).click();
    await expect(page).toHaveURL("/login");
  });
});
