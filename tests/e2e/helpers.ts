import { APIRequestContext, expect } from "@playwright/test";

const BASE = "http://localhost:8000";

// ── Auth ──────────────────────────────────────────────

export async function registerUser(
  request: APIRequestContext,
  email: string,
  password: string,
  fullName = "测试用户",
) {
  const res = await request.post(`${BASE}/api/v1/users/`, {
    data: { email, password, full_name: fullName },
  });
  // 200 = created, 400 = already exists — both are fine
  return res;
}

export async function loginUser(
  request: APIRequestContext,
  email: string,
  password: string,
): Promise<string> {
  const res = await request.post(`${BASE}/api/v1/users/login`, {
    data: { email, password },
  });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  return body.access_token;
}

// ── Projects ──────────────────────────────────────────

export interface ProjectData {
  name: string;
  description?: string;
  password?: string;
  llm_url?: string;
  llm_key?: string;
  llm_model?: string;
  lvm_url?: string;
  lvm_key?: string;
  lvm_model?: string;
}

export async function createProject(
  request: APIRequestContext,
  token: string,
  data: ProjectData,
) {
  const res = await request.post(`${BASE}/api/v1/projects/`, {
    headers: { Authorization: `Bearer ${token}` },
    data,
  });
  expect(res.ok()).toBeTruthy();
  return res.json();
}

export async function deleteProject(
  request: APIRequestContext,
  token: string,
  projectId: number,
) {
  await request.delete(`${BASE}/api/v1/projects/${projectId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function getProjects(request: APIRequestContext, token: string) {
  const res = await request.get(`${BASE}/api/v1/projects/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(res.ok()).toBeTruthy();
  return res.json();
}

// ── Agents ────────────────────────────────────────────

export interface AgentData {
  name: string;
  description?: string;
  tags?: string;
  icon?: string;
  gradient?: string;
  sort_order?: number;
  is_active?: boolean;
  is_placeholder?: boolean;
}

export async function createAgent(
  request: APIRequestContext,
  token: string,
  data: AgentData,
) {
  const res = await request.post(`${BASE}/api/v1/agents/`, {
    headers: { Authorization: `Bearer ${token}` },
    data,
  });
  expect(res.ok()).toBeTruthy();
  return res.json();
}

export async function deleteAgent(
  request: APIRequestContext,
  token: string,
  agentId: number,
) {
  await request.delete(`${BASE}/api/v1/agents/${agentId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function getAgents(request: APIRequestContext, token: string) {
  const res = await request.get(`${BASE}/api/v1/agents/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(res.ok()).toBeTruthy();
  return res.json();
}
