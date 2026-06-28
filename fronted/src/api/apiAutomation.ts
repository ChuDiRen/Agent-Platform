import { del, get, post } from './http'
import type { AgentTask } from './agentTask'
import { getPageItems, type PaginatedData } from './pagination'

export interface ApiRequestDetails {
  path: string
  method: string
  url_params: Record<string, unknown>
  form: Record<string, unknown>
  json: Record<string, unknown>
  cookies: Record<string, unknown>
  headers: Record<string, unknown>
}

export interface ApiAutomationCase {
  id: number
  project_id?: number | null
  module_id?: number | null
  module_name: string
  exec_type: string
  priority: number
  name: string
  request: ApiRequestDetails
  expected: string
  created_at?: string | null
}

export interface ApiExecutionResult {
  case_id: number
  case_name: string
  status: string
  expected: string
  ai_record: string
  response: {
    status_code: number
    headers: Record<string, unknown>
    body: unknown
  }
  request: ApiRequestDetails
}

export interface ApiExecutionDetails {
  summary: {
    success: number
    failed: number
    total: number
  }
  results: ApiExecutionResult[]
}

export interface ApiAutomationExec {
  id: number
  project_id?: number | null
  name: string
  exec_type: string
  case_ids: number[]
  details?: ApiExecutionDetails | null
  desc?: string | null
  exec_param: Record<string, unknown>
  exec_status: string
  created_at?: string | null
  updated_at?: string | null
}

export interface ApiAutomationExecPayload {
  project_id?: number | null
  name: string
  exec_type: string
  case_ids: number[]
  exec_param: Record<string, unknown>
  desc?: string | null
}

export interface ApiAutomationCaseQuery {
  project_id?: number
  name?: string
  priority?: number
  module_id?: number
  exec_type?: string
}

export function getApiAutomationCases(
  params?: ApiAutomationCaseQuery,
): Promise<ApiAutomationCase[]> {
  return get<PaginatedData<ApiAutomationCase>>('/api/v1/api-automation/cases', params).then(
    getPageItems,
  )
}

export function getApiAutomationCase(caseId: number): Promise<ApiAutomationCase> {
  return get<ApiAutomationCase>(`/api/v1/api-automation/cases/${caseId}`)
}

export function getApiAutomationExecs(projectId?: number): Promise<ApiAutomationExec[]> {
  return get<PaginatedData<ApiAutomationExec>>(
    '/api/v1/api-automation/execs',
    projectId ? { project_id: projectId } : undefined,
  ).then(getPageItems)
}

export function createApiAutomationExec(
  payload: ApiAutomationExecPayload,
): Promise<AgentTask<ApiExecutionDetails>> {
  return post<AgentTask<ApiExecutionDetails>>('/api/v1/api-automation/execs', payload)
}

export function copyApiAutomationExec(execId: number): Promise<ApiAutomationExec> {
  return post<ApiAutomationExec>(`/api/v1/api-automation/execs/${execId}/copy`)
}

export function deleteApiAutomationExec(execId: number): Promise<ApiAutomationExec> {
  return del<ApiAutomationExec>(`/api/v1/api-automation/execs/${execId}`)
}
