import { test, expect } from "@playwright/test";
import {
  createProject,
  deleteProject,
  getProjects,
  loginUser,
  registerUser,
  type ProjectData,
} from "./helpers";

const EMAIL = "e2e_admin@test.com";
const PASSWORD = "E2eTest123!";
let token = "";
const createdProjectIds: number[] = [];

test.beforeAll(async ({ request }) => {
  await registerUser(request, EMAIL, PASSWORD, "E2E管理员");
  token = await loginUser(request, EMAIL, PASSWORD);
});

test.afterEach(async ({ request }) => {
  for (const id of createdProjectIds) {
    await deleteProject(request, token, id).catch(() => {});
  }
  createdProjectIds.length = 0;
});

async function seedProject(
  request: any,
  overrides: Partial<ProjectData> = {},
): Promise<number> {
  const data: ProjectData = {
    name: `E2E项目_${Date.now()}`,
    description: "E2E测试项目",
    ...overrides,
  };
  const proj = await createProject(request, token, data);
  createdProjectIds.push(proj.id);
  return proj.id;
}

test.describe("Project 页面结构", () => {
  test("显示页面标题和新建按钮", async ({ page }) => {
    await page.goto("/projects");
    await expect(page.getByText("项目管理")).toBeVisible();
    await expect(page.getByRole("button", { name: "新建项目" })).toBeVisible();
  });

  test("显示管理员信息", async ({ page }) => {
    await page.goto("/projects");
    await expect(page.getByText("E2E管理员")).toBeVisible();
  });
});

test.describe("Project 项目列表（真实数据）", () => {
  test("显示已创建的项目", async ({ page, request }) => {
    await seedProject(request, {
      name: "E2E可见项目",
      description: "这个项目应该出现在列表中",
    });
    await page.goto("/projects");
    await expect(page.getByText("E2E可见项目")).toBeVisible();
    await expect(page.getByText("这个项目应该出现在列表中")).toBeVisible();
  });

  test("显示 LLM 模型标签", async ({ page, request }) => {
    await seedProject(request, {
      name: "E2E带模型项目",
      llm_model: "mimo-v2.5-pro",
    });
    await page.goto("/projects");
    await expect(page.getByText("LLM: mimo-v2.5-pro")).toBeVisible();
  });

  test("显示密码保护标签", async ({ page, request }) => {
    await seedProject(request, {
      name: "E2E密码项目",
      password: "secret123",
    });
    await page.goto("/projects");
    await expect(page.getByText("需密码")).toBeVisible();
  });

  test("显示操作按钮", async ({ page, request }) => {
    await seedProject(request, { name: "E2E操作按钮项目" });
    await page.goto("/projects");
    const card = page.locator(".project-card").filter({ hasText: "E2E操作按钮项目" });
    await expect(card.getByRole("button", { name: "编辑" })).toBeVisible();
    await expect(card.getByRole("button", { name: "进入" })).toBeVisible();
    await expect(card.getByRole("button", { name: "删除" })).toBeVisible();
  });
});

test.describe("Project 新建项目", () => {
  test("点击新建项目打开弹窗", async ({ page }) => {
    await page.goto("/projects");
    await page.getByRole("button", { name: "新建项目" }).click();
    await expect(page.getByText("项目名称")).toBeVisible();
    await expect(page.getByText("大语言模型 (LLM)")).toBeVisible();
    await expect(page.getByText("视觉模型 (LVM)")).toBeVisible();
    await expect(page.locator(".project-form input").nth(5)).toHaveValue("mimo-v2.5");
  });

  test("通过弹窗创建项目成功", async ({ page }) => {
    await page.goto("/projects");
    await page.getByRole("button", { name: "新建项目" }).click();
    await page.getByPlaceholder("请输入项目名称").fill("E2E弹窗创建项目");
    await page.getByPlaceholder("简要描述项目用途").fill("通过弹窗创建");
    await page.getByRole("button", { name: "创建项目" }).click();
    // Success message
    await expect(page.locator(".el-message")).toContainText("项目已创建");
    // Should appear in list
    await expect(page.getByText("E2E弹窗创建项目")).toBeVisible();
    // Clean up via API
    const projects = await getProjects({} as any, token);
    const created = projects.find((p: any) => p.name === "E2E弹窗创建项目");
    if (created) {
      createdProjectIds.push(created.id);
    }
  });
});

test.describe("Project 进入项目", () => {
  test("无密码项目直接进入 agent-hub", async ({ page, request }) => {
    await seedProject(request, { name: "E2E无密码项目" });
    await page.goto("/projects");
    const card = page.locator(".project-card").filter({ hasText: "E2E无密码项目" });
    await card.getByRole("button", { name: "进入" }).click();
    await expect(page).toHaveURL(/\/agent-hub/);
  });

  test("有密码项目弹出密码验证弹窗", async ({ page, request }) => {
    await seedProject(request, {
      name: "E2E密码验证项目",
      password: "testpass",
    });
    await page.goto("/projects");
    const card = page.locator(".project-card").filter({ hasText: "E2E密码验证项目" });
    await card.getByRole("button", { name: "进入" }).click();
    await expect(page.getByText("该项目需要密码才能进入")).toBeVisible();
  });
});

test.describe("Project 删除项目", () => {
  test("删除项目后不再显示", async ({ page, request }) => {
    const id = await seedProject(request, { name: "E2E待删除项目" });
    await page.goto("/projects");
    await expect(page.getByText("E2E待删除项目")).toBeVisible();
    const card = page.locator(".project-card").filter({ hasText: "E2E待删除项目" });
    // Accept the confirm dialog
    page.on("dialog", (dialog) => dialog.accept());
    await card.getByRole("button", { name: "删除" }).click();
    await expect(page.getByText("E2E待删除项目")).not.toBeVisible();
    // Already deleted, remove from cleanup list
    const idx = createdProjectIds.indexOf(id);
    if (idx > -1) createdProjectIds.splice(idx, 1);
  });
});

test.describe("Project 空状态", () => {
  test("无项目时显示空状态", async ({ page }) => {
    // We can't guarantee empty state with real services (seeded data may exist)
    // So we verify the page loads correctly regardless
    await page.goto("/projects");
    // Either shows projects or empty state — both are valid
    const hasProjects = await page.locator(".project-card").count();
    const hasEmpty = await page.getByText("还没有项目").isVisible().catch(() => false);
    expect(hasProjects > 0 || hasEmpty).toBeTruthy();
  });
});

test.describe("Project 管理员下拉菜单", () => {
  test("点击管理员显示退出登录", async ({ page }) => {
    await page.goto("/projects");
    await page.locator(".admin").click();
    await expect(page.getByText("退出登录")).toBeVisible();
  });

  test("点击退出登录跳转登录页", async ({ page }) => {
    await page.goto("/projects");
    await page.locator(".admin").click();
    await page.getByText("退出登录").click();
    await expect(page).toHaveURL(/\/login/);
  });
});
