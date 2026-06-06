import { del, get, post } from './http'

export interface UiActionStep {
  action: string
  target: string
  value: string
}

export interface UiAutomationCase {
  id: number
  project_id?: number | null
  module_id?: number | null
  module_name: string
  exec_type: string
  priority: number
  name: string
  page_url: string
  viewport: string
  steps: UiActionStep[]
  expected: string
  created_at?: string | null
}

export interface UiExecutionResult {
  case_id: number
  case_name: string
  status: string
  expected: string
  ai_record: string
  page_url: string
  screenshot: string
  steps: UiActionStep[]
  artifacts: Record<string, unknown>
}

export interface UiExecutionDetails {
  summary: {
    success: number
    failed: number
    total: number
  }
  results: UiExecutionResult[]
}

export interface UiAutomationExec {
  id: number
  project_id?: number | null
  name: string
  exec_type: string
  case_ids: number[]
  details?: UiExecutionDetails | null
  desc?: string | null
  exec_param: Record<string, unknown>
  exec_status: string
  created_at?: string | null
  updated_at?: string | null
}

export interface UiAutomationExecPayload {
  project_id?: number | null
  name: string
  exec_type: string
  case_ids: number[]
  exec_param: Record<string, unknown>
  desc?: string | null
}

export interface UiAutomationCaseQuery {
  project_id?: number
  name?: string
  priority?: number
  module_id?: number
  exec_type?: string
}

export function getUiAutomationCases(params?: UiAutomationCaseQuery): Promise<UiAutomationCase[]> {
  return get<UiAutomationCase[]>('/api/v1/ui-automation/cases', params)
}

export function getUiAutomationExecs(projectId?: number): Promise<UiAutomationExec[]> {
  return get<UiAutomationExec[]>('/api/v1/ui-automation/execs', projectId ? { project_id: projectId } : undefined)
}

export function createUiAutomationExec(payload: UiAutomationExecPayload): Promise<UiAutomationExec> {
  return post<UiAutomationExec>('/api/v1/ui-automation/execs', payload)
}

export function copyUiAutomationExec(execId: number): Promise<UiAutomationExec> {
  return post<UiAutomationExec>(`/api/v1/ui-automation/execs/${execId}/copy`)
}

export function deleteUiAutomationExec(execId: number): Promise<UiAutomationExec> {
  return del<UiAutomationExec>(`/api/v1/ui-automation/execs/${execId}`)
}
