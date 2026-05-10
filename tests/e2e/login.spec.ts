import { test, expect } from "@playwright/test";

test.describe("登录页面", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
  });

  test.describe("页面渲染", () => {
    test("显示品牌面板和表单", async ({ page }) => {
      await expect(page.getByText("Agent Platform")).toBeVisible();
      await expect(page.getByText("智能代理，无限可能")).toBeVisible();
      await expect(page.getByText("欢迎回来")).toBeVisible();
      await expect(page.getByText("登录以继续使用 Agent Platform")).toBeVisible();
    });

    test("显示三个功能特性", async ({ page }) => {
      await expect(page.getByText("多代理协同编排")).toBeVisible();
      await expect(page.getByText("可视化工作流引擎")).toBeVisible();
      await expect(page.getByText("实时监控与调试")).toBeVisible();
    });

    test("显示邮箱和密码输入框", async ({ page }) => {
      await expect(page.getByPlaceholder("邮箱地址")).toBeVisible();
      await expect(page.getByPlaceholder("密码")).toBeVisible();
    });

    test("显示登录按钮", async ({ page }) => {
      await expect(page.getByRole("button", { name: "登录" })).toBeVisible();
    });

    test("显示注册链接", async ({ page }) => {
      await expect(page.getByText("还没有账号？")).toBeVisible();
      await expect(page.getByRole("link", { name: "立即注册" })).toBeVisible();
    });
  });

  test.describe("表单验证", () => {
    test("邮箱和密码为空时显示提示", async ({ page }) => {
      await page.getByRole("button", { name: "登录" }).click();
      await expect(page.getByText("请输入邮箱和密码")).toBeVisible();
    });

    test("仅填写邮箱时显示提示", async ({ page }) => {
      await page.getByPlaceholder("邮箱地址").fill("test@example.com");
      await page.getByRole("button", { name: "登录" }).click();
      await expect(page.getByText("请输入邮箱和密码")).toBeVisible();
    });

    test("仅填写密码时显示提示", async ({ page }) => {
      await page.getByPlaceholder("密码").fill("password123");
      await page.getByRole("button", { name: "登录" }).click();
      await expect(page.getByText("请输入邮箱和密码")).toBeVisible();
    });
  });

  test.describe("登录流程", () => {
    test("登录成功后跳转到首页", async ({ page }) => {
      await page.route("**/api/v1/users/login", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            access_token: "test-token",
            token_type: "bearer",
            user: {
              id: 1,
              email: "test@example.com",
              full_name: "测试用户",
              is_superuser: false,
            },
          }),
        });
      });

      await page.getByPlaceholder("邮箱地址").fill("test@example.com");
      await page.getByPlaceholder("密码").fill("Test123456");
      await page.getByRole("button", { name: "登录" }).click();

      await page.waitForURL("/home");
      await expect(page).toHaveURL("/home");
    });

    test("登录成功后支持 redirect 参数跳转", async ({ page }) => {
      await page.route("**/api/v1/users/login", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            access_token: "test-token",
            token_type: "bearer",
            user: {
              id: 1,
              email: "test@example.com",
              full_name: "测试用户",
              is_superuser: false,
            },
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

    test("登录失败时显示错误信息", async ({ page }) => {
      await page.route("**/api/v1/users/login", async (route) => {
        await route.fulfill({
          status: 401,
          contentType: "application/json",
          body: JSON.stringify({ detail: "邮箱或密码错误" }),
        });
      });

      await page.getByPlaceholder("邮箱地址").fill("wrong@example.com");
      await page.getByPlaceholder("密码").fill("wrongpassword");
      await page.getByRole("button", { name: "登录" }).click();

      await expect(page.getByText("邮箱或密码错误")).toBeVisible();
    });

    test("登录按钮显示加载状态", async ({ page }) => {
      // Delay the API response to observe loading state
      await page.route("**/api/v1/users/login", async (route) => {
        await new Promise((r) => setTimeout(r, 1000));
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

      await page.getByPlaceholder("邮箱地址").fill("test@example.com");
      await page.getByPlaceholder("密码").fill("Test123456");
      await page.getByRole("button", { name: "登录" }).click();

      // Element Plus loading button should have aria-busy or loading class
      const btn = page.getByRole("button", { name: "登录" });
      await expect(btn).toBeDisabled();
    });
  });

  test.describe("导航", () => {
    test("点击注册链接跳转到注册页", async ({ page }) => {
      await page.getByRole("link", { name: "立即注册" }).click();
      await expect(page).toHaveURL("/register");
    });
  });
});
