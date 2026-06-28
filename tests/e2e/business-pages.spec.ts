import { test, expect } from "@playwright/test";
import {
  createAgentTask,
  createApiDocument,
  createProject,
  createRequirementDocument,
  createTestCase,
  deleteApiDocument,
  deleteProject,
  deleteRequirementDocument,
  deleteTestCase,
  loginUser,
  registerUser,
} from "./helpers";

const EMAIL = `e2e_business_pages_${Date.now()}@test.com`;
const PASSWORD = "BusinessPages123!";
let token = "";
let projectId = 0;
const requirementDocumentIds: number[] = [];
const apiDocumentIds: number[] = [];
const testCaseIds: number[] = [];

test.beforeAll(async ({ request }) => {
  await registerUser(request, EMAIL, PASSWORD, "业务页测试用户");
  token = await loginUser(request, EMAIL, PASSWORD);
  const project = await createProject(request, token, {
    name: `E2E业务页项目_${Date.now()}`,
    description: "覆盖 Agent 业务页真实链路",
  });
  projectId = project.id;
});

test.afterAll(async ({ request }) => {
  for (const id of testCaseIds) await deleteTestCase(request, token, id).catch(() => {});
  for (const id of apiDocumentIds) await deleteApiDocument(request, token, id).catch(() => {});
  for (const id of requirementDocumentIds) {
    await deleteRequirementDocument(request, token, id).catch(() => {});
  }
  if (projectId) await deleteProject(request, token, projectId).catch(() => {});
});

async function expectMessage(page: import("@playwright/test").Page, text: string) {
  await expect(page.locator(".el-message").filter({ hasText: text }).last()).toBeVisible();
}

function withProject(path: string) {
  return `${path}?projectId=${projectId}`;
}

test.describe("Agent 业务页真实 E2E 覆盖", () => {
  test("测试数据生成页可保存模板并提交生成任务", async ({ page }) => {
    await page.goto(withProject("/test-data-generator"));

    await expect(page.getByText("AI测试数据生成系统")).toBeVisible();
    await page.getByPlaceholder("输入你期望的数据特征、约束或额外要求").fill("生成真实注册账号数据");
    await page.getByRole("button", { name: "保存为模板" }).click();
    await expectMessage(page, "模板已保存");

    await page.getByRole("button", { name: "运行生成" }).click();
    await expect(page.locator(".success-bar").filter({ hasText: "生成成功" }).first()).toBeVisible();
  });

  test("需求评审页可展示文档并提交 AI 需求评审", async ({ page, request }) => {
    const root = await createRequirementDocument(request, token, {
      project_id: projectId,
      name: "业务需求目录",
      title: "业务需求目录",
      is_directory: true,
    });
    requirementDocumentIds.push(root.id);
    const doc = await createRequirementDocument(request, token, {
      project_id: projectId,
      parent_id: root.id,
      name: "登录需求",
      title: "登录需求",
      content: "# 登录需求\n用户输入邮箱和密码后登录系统，失败时展示错误提示。",
      is_directory: false,
    });
    requirementDocumentIds.push(doc.id);

    await page.goto(withProject("/requirement-review"));

    await expect(page.locator(".node-name", { hasText: "登录需求" }).first()).toBeVisible();
    await page.locator(".tree-row.child", { hasText: "登录需求" }).first().click();
    await expect(page.getByPlaceholder("请选择或导入需求文档，在此编辑详细说明。")).toHaveValue(/登录需求/);
    await page.getByRole("button", { name: "AI需求评审" }).click();
    await expect(page.getByText("AI正在处理...")).toBeVisible();
  });

  test("接口文档分析页可展示文档并提交 AI 文档评审", async ({ page, request }) => {
    const root = await createApiDocument(request, token, {
      project_id: projectId,
      name: "接口文档目录",
      title: "接口文档目录",
      is_directory: true,
    });
    apiDocumentIds.push(root.id);
    const doc = await createApiDocument(request, token, {
      project_id: projectId,
      parent_id: root.id,
      name: "登录接口",
      title: "登录接口",
      content: "POST /api/v1/users/login\n请求体包含 email 和 password。",
      is_directory: false,
    });
    apiDocumentIds.push(doc.id);

    await page.goto(withProject("/interface-document-analysis"));

    await expect(page.locator(".doc-name", { hasText: "登录接口" }).first()).toBeVisible();
    await page.locator(".doc-row.child", { hasText: "登录接口" }).first().click();
    await expect(page.getByPlaceholder("请选择或导入接口文档，在此编辑接口说明。")).toHaveValue(/POST \/api\/v1\/users\/login/);
    await page.getByRole("button", { name: "AI 接口评审" }).click();
    await page.getByRole("button", { name: "立即开始 AI 文档评审" }).click();
    await expectMessage(page, "任务已提交");
  });

  test("AI 接口用例页可展示用例并支持手动新增", async ({ page, request }) => {
    const existing = await createTestCase(request, token, {
      project_id: projectId,
      module_id: 4101,
      name: "登录成功接口用例",
      priority: 1,
      precondition: "用户已注册",
      steps: "POST /api/v1/users/login",
      expected: "返回 access_token",
    });
    testCaseIds.push(existing.id);

    await page.goto(withProject("/ai-test-cases"));

    await expect(page.getByText("登录成功接口用例")).toBeVisible();
    await page.getByRole("button", { name: "手动新增" }).click();
    await expect(page.locator(".el-dialog")).toBeVisible();
    await expect(page.locator(".el-dialog input").first()).toBeVisible();
  });

  test("UI 自动化页可加载空用例列表并提示选择用例", async ({ page }) => {
    await page.goto(withProject("/ui-automation"));

    await expect(page.getByText("UI自动化助手")).toBeVisible();
    await expect(page.getByPlaceholder("请输入UI用例名称")).toBeVisible();
    await page.getByRole("button", { name: "创建 AI 测试任务" }).click();
    await expectMessage(page, "请先勾选需要执行的UI用例");
  });

  test("API 自动化页可加载空用例列表并提示选择用例", async ({ page }) => {
    await page.goto(withProject("/api-automation"));

    await expect(page.getByText("接口自动化助手")).toBeVisible();
    await expect(page.getByPlaceholder("请输入用例名称")).toBeVisible();
    await page.getByRole("button", { name: "创建 AI 测试任务" }).click();
    await expectMessage(page, "请先勾选需要执行的接口用例");
  });

  test("性能分析页可填写压测指标并提交分析任务", async ({ page }) => {
    await page.goto(withProject("/performance-analysis"));

    await expect(page.getByText("AI性能数据分析助手")).toBeVisible();
    await page.locator(".config-form").getByLabel("报告名称").fill("登录接口压测");
    await page.locator(".config-form").getByLabel("测试场景").fill("高峰登录");
    await page.locator(".config-form textarea").fill("avg 860ms, P95 1700ms, error 2.5%");
    await page.getByPlaceholder("指标名称").fill("P95响应时间");
    await page.getByRole("button", { name: "开始 AI 分析" }).click();
    await expect(page.locator(".el-message").last()).toBeVisible();
  });

  test("Agent 任务中心可展示真实任务详情", async ({ page, request }) => {
    const task = await createAgentTask(request, token, {
      agent_key: "test_data",
      project_id: projectId,
      input_payload: {
        count: 1,
        format: "json",
        lang: "zh",
        fields: [{ name: "email", type: "email", rule: "测试账号" }],
      },
    });

    await page.goto(`/agent-tasks?task_id=${task.id}`);

    await expect(page.getByText(`任务 #${task.id}`)).toBeVisible();
    await expect(page.getByText(new RegExp(`#${task.id} · test_data`))).toBeVisible();
    await expect(page.getByRole("heading", { name: "执行事件" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "结果" })).toBeVisible();
  });
});