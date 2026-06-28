import { test, expect } from "@playwright/test";
import { createProject, deleteProject, loginUser, registerUser } from "./helpers";

const EMAIL = "e2e_auth_context@test.com";
const PASSWORD = "AuthContext123!";
let token = "";
const createdProjectIds: number[] = [];

test.beforeAll(async ({ request }) => {
  await registerUser(request, EMAIL, PASSWORD, "认证上下文测试用户");
  token = await loginUser(request, EMAIL, PASSWORD);
});

test.afterEach(async ({ request }) => {
  for (const id of createdProjectIds) {
    await deleteProject(request, token, id).catch(() => {});
  }
  createdProjectIds.length = 0;
});

async function seedProject(request: Parameters<typeof createProject>[0], name: string) {
  const project = await createProject(request, token, {
    name,
    description: "真实浏览器项目上下文测试",
  });
  createdProjectIds.push(project.id);
  return project;
}

async function setBrowserAuth(page: import("@playwright/test").Page) {
  await page.context().addCookies([
    {
      name: "vue3_token",
      value: token,
      domain: "localhost",
      path: "/",
    },
  ]);
  await page.addInitScript((auth) => {
    localStorage.setItem(
      "user_info",
      JSON.stringify({
        token: auth.token,
        userName: "认证上下文测试用户",
        avatar: "",
        role: "user",
      }),
    );
  }, { token });
}

test.describe("认证与项目上下文真实浏览器链路", () => {
  test("未登录访问受保护页会跳转登录并保留 redirect", async ({ page }) => {
    await page.context().clearCookies();
    await page.goto("/login");
    await page.evaluate(() => localStorage.clear());

    await page.goto("/agent-hub?projectId=123");

    await expect(page).toHaveURL(/\/login\?redirect=/);
    const url = new URL(page.url());
    expect(url.searchParams.get("redirect")).toBe("/agent-hub?projectId=123");
  });

  test("过期 token 触发真实 401 后清理状态并带 redirect 回登录", async ({ page }) => {
    await page.context().addCookies([
      {
        name: "vue3_token",
        value: "invalid-token-for-real-401-flow",
        domain: "localhost",
        path: "/",
      },
    ]);
    await page.addInitScript(() => {
      localStorage.setItem(
        "user_info",
        JSON.stringify({ token: "stale", userName: "过期用户", avatar: "", role: "user" }),
      );
    });

    const failedProjects = page.waitForResponse(
      (response) => response.url().includes("/api/v1/projects") && response.status() === 401,
    );
    await page.goto("/projects");
    await failedProjects;

    await expect(page).toHaveURL(/\/login\?redirect=/);
    const url = new URL(page.url());
    expect(url.searchParams.get("redirect")).toBe("/projects");
    expect(await page.evaluate(() => localStorage.getItem("user_info"))).not.toContain("过期用户");
  });

  test("从项目卡片进入 AgentHub 时携带真实 projectId", async ({ page, request }) => {
    const project = await seedProject(request, `真实上下文项目_${Date.now()}`);
    await setBrowserAuth(page);

    await page.goto("/projects");
    const card = page.locator(".project-card").filter({ hasText: project.name });
    await card.getByRole("button", { name: "进入" }).click();

    await expect(page).toHaveURL(new RegExp(`/agent-hub\\?projectId=${project.id}$`));
  });

  test("Agent 页面缺失 projectId 时回到项目管理", async ({ page }) => {
    await setBrowserAuth(page);

    await page.goto("/ai-test-cases");

    await expect(page).toHaveURL(/\/projects$/);
  });
});