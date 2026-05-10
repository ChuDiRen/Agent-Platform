import { test, expect } from "@playwright/test";

test.describe("首页", () => {
  test.use({ storageState: ".auth/user.json" });

  test.beforeEach(async ({ page }) => {
    await page.goto("/home");
  });

  test.describe("页面渲染", () => {
    test("显示顶部导航栏和 Logo", async ({ page }) => {
      await expect(page.getByText("Agent Platform")).toBeVisible();
    });

    test("显示用户信息", async ({ page }) => {
      await expect(page.getByText("测试用户")).toBeVisible();
    });

    test("管理员显示 Admin 角色标签", async ({ page }) => {
      await expect(page.getByText("Admin")).toBeVisible();
    });

    test("显示欢迎信息", async ({ page }) => {
      await expect(page.getByText("你好，")).toBeVisible();
      await expect(page.getByText("测试用户").first()).toBeVisible();
      await expect(page.getByText("欢迎回到 Agent Platform，今天想创建什么？")).toBeVisible();
    });

    test("显示四个快速操作卡片", async ({ page }) => {
      await expect(page.getByText("创建代理")).toBeVisible();
      await expect(page.getByText("从零开始构建智能代理")).toBeVisible();
      await expect(page.getByText("工作流")).toBeVisible();
      await expect(page.getByText("设计多代理协同流程")).toBeVisible();
      await expect(page.getByText("模板库")).toBeVisible();
      await expect(page.getByText("使用预置模板快速开始")).toBeVisible();
      await expect(page.getByText("数据源")).toBeVisible();
      await expect(page.getByText("连接外部数据与服务")).toBeVisible();
    });

    test("显示状态栏信息", async ({ page }) => {
      await expect(page.getByText("系统状态")).toBeVisible();
      await expect(page.getByText("运行中")).toBeVisible();
      await expect(page.getByText("活跃代理")).toBeVisible();
      await expect(page.getByText("今日任务")).toBeVisible();
      await expect(page.getByText("角色")).toBeVisible();
      await expect(page.getByText("管理员")).toBeVisible();
    });
  });

  test.describe("登出功能", () => {
    test("点击登出按钮跳转到登录页", async ({ page }) => {
      await page.locator(".logout-btn").click();
      await page.waitForURL("/login");
      await expect(page).toHaveURL("/login");
      await expect(page.getByText("已退出登录")).toBeVisible();
    });
  });
});
