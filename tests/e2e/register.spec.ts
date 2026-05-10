import { test, expect } from "@playwright/test";

test.describe("注册页面", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/register");
  });

  test.describe("页面渲染", () => {
    test("显示品牌面板和表单", async ({ page }) => {
      await expect(page.getByText("Agent Platform")).toBeVisible();
      await expect(page.getByText("加入我们，开启智能之旅")).toBeVisible();
      await expect(page.getByText("创建账号")).toBeVisible();
      await expect(page.getByText("注册以开始使用 Agent Platform")).toBeVisible();
    });

    test("显示品牌统计数据", async ({ page }) => {
      await expect(page.getByText("10K+")).toBeVisible();
      await expect(page.getByText("活跃用户")).toBeVisible();
      await expect(page.getByText("500+")).toBeVisible();
      await expect(page.getByText("代理模板")).toBeVisible();
      await expect(page.getByText("99.9%")).toBeVisible();
      await expect(page.getByText("可用性")).toBeVisible();
    });

    test("显示所有表单输入框", async ({ page }) => {
      await expect(page.getByPlaceholder("邮箱地址")).toBeVisible();
      await expect(page.getByPlaceholder("姓名（可选）")).toBeVisible();
      await expect(page.getByPlaceholder("设置密码")).toBeVisible();
      await expect(page.getByPlaceholder("确认密码")).toBeVisible();
    });

    test("显示注册按钮", async ({ page }) => {
      await expect(page.getByRole("button", { name: "注册" })).toBeVisible();
    });

    test("显示返回登录链接", async ({ page }) => {
      await expect(page.getByText("已有账号？")).toBeVisible();
      await expect(page.getByRole("link", { name: "返回登录" })).toBeVisible();
    });
  });

  test.describe("表单验证", () => {
    test("必填字段为空时显示提示", async ({ page }) => {
      await page.getByRole("button", { name: "注册" }).click();
      await expect(page.getByText("请填写完整信息")).toBeVisible();
    });

    test("密码不一致时显示提示", async ({ page }) => {
      await page.getByPlaceholder("邮箱地址").fill("new@example.com");
      await page.getByPlaceholder("设置密码").fill("Password123");
      await page.getByPlaceholder("确认密码").fill("Password456");
      await page.getByRole("button", { name: "注册" }).click();
      await expect(page.getByText("两次密码不一致")).toBeVisible();
    });

    test("仅缺少确认密码时显示提示", async ({ page }) => {
      await page.getByPlaceholder("邮箱地址").fill("new@example.com");
      await page.getByPlaceholder("设置密码").fill("Password123");
      await page.getByRole("button", { name: "注册" }).click();
      await expect(page.getByText("请填写完整信息")).toBeVisible();
    });
  });

  test.describe("注册流程", () => {
    test("注册成功后跳转到登录页", async ({ page }) => {
      await page.route("**/api/v1/users/", async (route) => {
        if (route.request().method() === "POST") {
          await route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify({
              id: 2,
              email: "new@example.com",
              full_name: "新用户",
            }),
          });
        } else {
          await route.continue();
        }
      });

      await page.getByPlaceholder("邮箱地址").fill("new@example.com");
      await page.getByPlaceholder("姓名（可选）").fill("新用户");
      await page.getByPlaceholder("设置密码").fill("Password123");
      await page.getByPlaceholder("确认密码").fill("Password123");
      await page.getByRole("button", { name: "注册" }).click();

      await page.waitForURL("/login");
      await expect(page).toHaveURL("/login");
      await expect(page.getByText("注册成功，请登录")).toBeVisible();
    });

    test("注册失败时显示错误信息", async ({ page }) => {
      await page.route("**/api/v1/users/", async (route) => {
        if (route.request().method() === "POST") {
          await route.fulfill({
            status: 400,
            contentType: "application/json",
            body: JSON.stringify({ detail: "该邮箱已被注册" }),
          });
        } else {
          await route.continue();
        }
      });

      await page.getByPlaceholder("邮箱地址").fill("existing@example.com");
      await page.getByPlaceholder("设置密码").fill("Password123");
      await page.getByPlaceholder("确认密码").fill("Password123");
      await page.getByRole("button", { name: "注册" }).click();

      await expect(page.getByText("该邮箱已被注册")).toBeVisible();
    });

    test("注册按钮显示加载状态", async ({ page }) => {
      await page.route("**/api/v1/users/", async (route) => {
        if (route.request().method() === "POST") {
          await new Promise((r) => setTimeout(r, 1000));
          await route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify({ id: 2, email: "new@example.com" }),
          });
        } else {
          await route.continue();
        }
      });

      await page.getByPlaceholder("邮箱地址").fill("new@example.com");
      await page.getByPlaceholder("设置密码").fill("Password123");
      await page.getByPlaceholder("确认密码").fill("Password123");
      await page.getByRole("button", { name: "注册" }).click();

      const btn = page.getByRole("button", { name: "注册" });
      await expect(btn).toBeDisabled();
    });
  });

  test.describe("导航", () => {
    test("点击返回登录链接跳转到登录页", async ({ page }) => {
      await page.getByRole("link", { name: "返回登录" }).click();
      await expect(page).toHaveURL("/login");
    });
  });
});
