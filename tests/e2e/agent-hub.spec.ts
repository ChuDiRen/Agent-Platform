import { test, expect } from "@playwright/test";
import {
  getAgents,
  createAgent,
  deleteAgent,
  loginUser,
  registerUser,
  type AgentData,
} from "./helpers";

const EMAIL = "e2e_admin@test.com";
const PASSWORD = "E2eTest123!";
let token = "";
const createdAgentIds: number[] = [];

test.beforeAll(async ({ request }) => {
  token = await loginUser(request, "admin@qq.com", "admin123456");
});

test.afterEach(async ({ request }) => {
  // Clean up agents created during the test
  for (const id of createdAgentIds) {
    await deleteAgent(request, token, id).catch(() => {});
  }
  createdAgentIds.length = 0;
});

async function seedAgent(
  request: any,
  overrides: Partial<AgentData> = {},
): Promise<number> {
  const data: AgentData = {
    name: `E2E智能体_${Date.now()}`,
    description: "E2E测试用智能体",
    tags: JSON.stringify(["测试标签A", "测试标签B"]),
    icon: "doc",
    gradient: "linear-gradient(135deg, #3b82f6, #6366f1)",
    sort_order: 99,
    is_active: true,
    is_placeholder: false,
    ...overrides,
  };
  const agent = await createAgent(request, token, data);
  createdAgentIds.push(agent.id);
  return agent.id;
}

test.describe("AgentHub 页面结构", () => {
  test("显示主标题和副标题", async ({ page }) => {
    await page.goto("/agent-hub");
    await expect(page.locator(".hero h1")).toContainText("智能");
    await expect(page.locator(".hero h1")).toContainText("数字员工");
    await expect(page.locator(".hero h1")).toContainText("降本增效");
    await expect(
      page.getByText("AI驱动的全链路测试工具平台"),
    ).toBeVisible();
  });

  test("显示 logo 和管理员信息", async ({ page }) => {
    await page.goto("/agent-hub");
    await expect(page.getByText("大熊AI智能体", { exact: true })).toBeVisible();
    await expect(page.getByText("E2E管理员")).toBeVisible();
  });

  test("显示退出项目按钮", async ({ page }) => {
    await page.goto("/agent-hub");
    await expect(
      page.getByRole("button", { name: "退出项目" }),
    ).toBeVisible();
  });
});

test.describe("AgentHub 智能体卡片（真实数据）", () => {
  test("显示种子智能体卡片", async ({ page }) => {
    await page.goto("/agent-hub");
    // These are seeded by the backend on startup
    await expect(page.getByText("AI需求评估助手")).toBeVisible();
    await expect(page.getByText("AI测试用例智能体")).toBeVisible();
    await expect(page.getByText("更多智能体即将上线")).toBeVisible();
  });

  test("显示功能标签", async ({ page }) => {
    await page.goto("/agent-hub");
    await expect(page.getByText("需求分析")).toBeVisible();
    await expect(page.getByText("文档管理")).toBeVisible();
  });

  test("新建智能体后出现在页面", async ({ page, request }) => {
    await seedAgent(request, {
      name: "E2E新建智能体",
      description: "通过API创建后在页面验证",
      tags: JSON.stringify(["新建标签"]),
    });
    await page.goto("/agent-hub");
    await expect(page.getByText("E2E新建智能体")).toBeVisible();
    await expect(page.getByText("新建标签")).toBeVisible();
  });

  test("占位智能体显示敬请期待按钮", async ({ page }) => {
    await page.goto("/agent-hub");
    const placeholder = page
      .locator(".card")
      .filter({ hasText: "更多智能体即将上线" });
    await expect(placeholder.getByRole("button", { name: "敬请期待" })).toBeVisible();
  });
});

test.describe("AgentHub 交互", () => {
  test("点击立即使用进入真实业务页", async ({ page }) => {
    await page.goto("/agent-hub");
    await page.getByRole("button", { name: "立即使用" }).first().click();
    await expect(page).not.toHaveURL(/\/agent-hub$/);
  });

  test("点击敬请期待显示 ElMessage", async ({ page }) => {
    await page.goto("/agent-hub");
    await page.getByRole("button", { name: "敬请期待" }).click();
    await expect(page.locator(".el-message").filter({ hasText: "敬请期待" }).last()).toBeVisible();
  });

  test("点击退出项目显示 ElMessage 并跳转", async ({ page }) => {
    await page.goto("/agent-hub");
    await page.getByRole("button", { name: "退出项目" }).click();
    await expect(page.locator(".el-message")).toContainText("退出项目");
    await expect(page).toHaveURL(/\/projects/);
  });
});

test.describe("AgentHub 管理员下拉菜单", () => {
  test("点击管理员显示下拉菜单", async ({ page }) => {
    await page.goto("/agent-hub");
    await page.locator(".admin").click();
    await expect(page.getByText("退出登录")).toBeVisible();
  });

  test("点击退出登录跳转登录页", async ({ page }) => {
    await page.goto("/agent-hub");
    await page.locator(".admin").click();
    await page.getByText("退出登录").click();
    await expect(page).toHaveURL(/\/login/);
  });
});
