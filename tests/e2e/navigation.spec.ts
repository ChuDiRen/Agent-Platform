import { test, expect } from "@playwright/test";
import { registerUser, loginUser } from "./helpers";

const EMAIL = "e2e_nav@test.com";
const PASSWORD = "NavTest123!";

test.describe("页面导航", () => {
  test.beforeAll(async ({ request }) => {
    await registerUser(request, EMAIL, PASSWORD, "导航测试");
  });

  test("未登录时访问受保护页面跳转登录", async ({ page }) => {
    await page.context().clearCookies();
    await page.addInitScript(() => localStorage.clear());
    await page.goto("/projects");
    await expect(page).toHaveURL(/\/login/);
  });

  test("登录后可访问项目管理", async ({ page, request }) => {
    const token = await loginUser(request, EMAIL, PASSWORD);
    await page.addInitScript((t) => {
      localStorage.setItem("user_info", JSON.stringify({
        token: t,
        userName: "导航测试",
        avatar: "",
        role: "admin",
      }));
    }, token);
    await page.goto("/projects");
    await expect(page.getByText("项目管理")).toBeVisible();
  });

  test("登录后可访问 agent-hub", async ({ page, request }) => {
    const token = await loginUser(request, EMAIL, PASSWORD);
    await page.addInitScript((t) => {
      localStorage.setItem("user_info", JSON.stringify({
        token: t,
        userName: "导航测试",
        avatar: "",
        role: "admin",
      }));
    }, token);
    await page.goto("/agent-hub");
    await expect(page.getByText("大熊AI智能体", { exact: true })).toBeVisible();
  });

  test("从项目管理进入 agent-hub", async ({ page, request }) => {
    const token = await loginUser(request, EMAIL, PASSWORD);
    await page.addInitScript((t) => {
      localStorage.setItem("user_info", JSON.stringify({
        token: t,
        userName: "导航测试",
        avatar: "",
        role: "admin",
      }));
    }, token);
    await page.goto("/projects");
    // Click enter on first project card
    const enterBtn = page.locator(".action-enter").first();
    if (await enterBtn.isVisible().catch(() => false)) {
      await enterBtn.click();
      await expect(page).toHaveURL(/\/agent-hub\?projectId=\d+/);
    }
  });
});
