import { del, get, post, put } from './http'
import type { AgentTask } from './agentTask'
import { getPageItems, type PaginatedData } from './pagination'

export interface RequirementModule {
  id: number
  title: string
  content: string
}

export interface TestCase {
  id: number
  project_id?: number | null
  module_id?: number | null
  name: string
  priority: number
  precondition?: string | null
  steps?: string | null
  expected?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export interface TestCasePayload {
  project_id?: number | null
  module_id?: number | null
  name: string
  priority: number
  precondition?: string | null
  steps?: string | null
  expected?: string | null
}

export interface TestCaseGenerateRequest {
  project_id?: number | null
  module: RequirementModule
  extra_requirement?: string
}

export interface TestCaseGenerateResponse {
  cases: TestCasePayload[]
  elapsed_ms: number
}

export function getTestCases(params?: {
  project_id?: number
  module_id?: number
}): Promise<TestCase[]> {
  return get<PaginatedData<TestCase>>('/api/v1/test-cases/', params).then(getPageItems)
}

export function createTestCase(data: TestCasePayload): Promise<TestCase> {
  return post<TestCase>('/api/v1/test-cases/', data)
}

export function updateTestCase(id: number, data: Partial<TestCasePayload>): Promise<TestCase> {
  return put<TestCase>(`/api/v1/test-cases/${id}`, data)
}

export function deleteTestCase(id: number): Promise<TestCase> {
  return del<TestCase>(`/api/v1/test-cases/${id}`)
}

export function generateTestCases(
  data: TestCaseGenerateRequest,
): Promise<AgentTask<TestCaseGenerateResponse>> {
  return post<AgentTask<TestCaseGenerateResponse>>('/api/v1/test-cases/generate', data)
}

export function applyGeneratedTestCases(cases: TestCasePayload[]): Promise<TestCase[]> {
  return post<TestCase[]>('/api/v1/test-cases/apply', { cases })
}
