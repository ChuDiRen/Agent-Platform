import { get, post } from './http'

export type AgentTaskStatus = 'created' | 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled'

export interface AgentTask<TOutput = unknown> {
  id: number
  agent_key: string
  project_id?: number | null
  user_id?: number | null
  status: AgentTaskStatus
  priority: number
  input_payload: Record<string, unknown>
  result_payload?: {
    summary?: string
    output?: TOutput
    artifacts?: AgentArtifact[]
  } | null
  error_message?: string | null
  retry_count: number
  started_at?: string | null
  finished_at?: string | null
  created_at: string
  updated_at: string
}

export interface AgentTaskEvent {
  id: number
  task_id: number
  event_type: string
  message: string
  progress?: number | null
  payload?: Record<string, unknown> | null
  created_at: string
}

export interface AgentArtifact {
  id?: number
  task_id?: number
  name: string
  artifact_type: string
  storage_path: string
  mime_type?: string | null
  size_bytes?: number | null
  created_at?: string
}

export interface AgentTaskCreateRequest {
  agent_key: string
  project_id?: number | null
  user_id?: number | null
  priority?: number
  input_payload: Record<string, unknown>
}

export interface AgentTaskListResponse<TOutput = unknown> {
  items: AgentTask<TOutput>[]
  total: number
  page: number
  page_size: number
}

export interface AgentTaskQuery {
  agent_key?: string
  status?: AgentTaskStatus
  project_id?: number
  skip?: number
  limit?: number
}

export function createAgentTask<TOutput = unknown>(data: AgentTaskCreateRequest): Promise<AgentTask<TOutput>> {
  return post<AgentTask<TOutput>>('/api/v1/agent-tasks/', data)
}

export function getAgentTasks<TOutput = unknown>(params?: AgentTaskQuery): Promise<AgentTaskListResponse<TOutput>> {
  return get<AgentTaskListResponse<TOutput>>('/api/v1/agent-tasks/', params)
}

export function getAgentTask<TOutput = unknown>(taskId: number): Promise<AgentTask<TOutput>> {
  return get<AgentTask<TOutput>>(`/api/v1/agent-tasks/${taskId}`)
}

export function getAgentTaskEvents(taskId: number): Promise<AgentTaskEvent[]> {
  return get<AgentTaskEvent[]>(`/api/v1/agent-tasks/${taskId}/events`)
}

export function getAgentTaskArtifacts(taskId: number): Promise<AgentArtifact[]> {
  return get<AgentArtifact[]>(`/api/v1/agent-tasks/${taskId}/artifacts`)
}

export function retryAgentTask<TOutput = unknown>(taskId: number): Promise<AgentTask<TOutput>> {
  return post<AgentTask<TOutput>>(`/api/v1/agent-tasks/${taskId}/retry`)
}

export function cancelAgentTask<TOutput = unknown>(taskId: number): Promise<AgentTask<TOutput>> {
  return post<AgentTask<TOutput>>(`/api/v1/agent-tasks/${taskId}/cancel`)
}
