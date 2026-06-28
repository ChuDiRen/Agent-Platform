import { del, get, post, put } from './http'
import type { AgentTask } from './agentTask'
import { getPageItems, type PaginatedData } from './pagination'

export type TestDataFieldType = 'number' | 'string' | 'email' | 'phone' | 'date' | 'boolean'
export type TestDataFormat = 'json' | 'csv'
export type TestDataLanguage = 'zh' | 'en'

export interface TestDataField {
  name: string
  type: TestDataFieldType
  rule: string
}

export interface TestDataGenerateRequest {
  fields: TestDataField[]
  hint?: string
  count: number
  format: TestDataFormat
  lang: TestDataLanguage
}

export interface TestDataGenerateResponse {
  data: Record<string, unknown>[]
  content: string
  format: TestDataFormat
  count: number
  elapsed_ms: number
}

export interface TestDataTemplate extends TestDataGenerateRequest {
  id: number
  project_id?: number | null
  name: string
  description?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export interface TestDataTemplatePayload extends TestDataGenerateRequest {
  project_id?: number | null
  name: string
  description?: string | null
}

export function generateTestData(
  data: TestDataGenerateRequest,
): Promise<AgentTask<TestDataGenerateResponse>> {
  return post<AgentTask<TestDataGenerateResponse>>('/api/v1/test-data/generate', data)
}

export function getTestDataTemplates(projectId?: number): Promise<TestDataTemplate[]> {
  return get<PaginatedData<TestDataTemplate>>(
    '/api/v1/test-data/templates/',
    projectId ? { project_id: projectId } : undefined,
  ).then(getPageItems)
}

export function createTestDataTemplate(data: TestDataTemplatePayload): Promise<TestDataTemplate> {
  return post<TestDataTemplate>('/api/v1/test-data/templates/', data)
}

export function updateTestDataTemplate(
  templateId: number,
  data: Partial<TestDataTemplatePayload>,
): Promise<TestDataTemplate> {
  return put<TestDataTemplate>(`/api/v1/test-data/templates/${templateId}`, data)
}

export function deleteTestDataTemplate(templateId: number): Promise<TestDataTemplate> {
  return del<TestDataTemplate>(`/api/v1/test-data/templates/${templateId}`)
}
