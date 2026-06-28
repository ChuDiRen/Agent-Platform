import { test, expect } from "@playwright/test";
import { registerUser } from "./helpers";

const EMAIL = "e2e_login_test@test.com";
const PASSWORD = "LoginTest123!";

test.describe("登录页面", () => {
  test.beforeAll(async ({ request }) => {
    await registerUser(request, EMAIL, PASSWORD, "登录测试用户");
  });

  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.addInitScript(() => localStorage.clear());
    await page.goto("/login", { waitUntil: "domcontentloaded" });
  });

  test.describe("页面结构", () => {
    test("显示登录表单", async ({ page }) => {
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

  test.describe("登录流程（真实后端）", () => {
    test("登录成功后跳转到项目管理", async ({ page }) => {
      await page.getByPlaceholder("邮箱地址").fill(EMAIL);
      await page.getByPlaceholder("密码").fill(PASSWORD);
      await page.getByRole("button", { name: "登录" }).click();
      await page.waitForURL("/projects");
      await expect(page).toHaveURL("/projects");
    });

    test("登录失败时显示错误信息", async ({ page }) => {
      await page.getByPlaceholder("邮箱地址").fill("wrong@test.com");
      await page.getByPlaceholder("密码").fill("wrongpassword");
      await page.getByRole("button", { name: "登录" }).click();
      await expect(page.locator(".el-message--error, .el-message").last()).toBeVisible();
    });
  });

  test.describe("导航", () => {
    test("点击注册链接跳转到注册页", async ({ page }) => {
      await page.getByRole("link", { name: "立即注册" }).click();
      await expect(page).toHaveURL("/register");
    });
  });
});
