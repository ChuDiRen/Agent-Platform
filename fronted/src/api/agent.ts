import { get } from './http'

export interface AgentInfo {
  id: number
  name: string
  description?: string
  tags?: string
  icon?: string
  gradient?: string
  sort_order: number
  is_active: boolean
  is_placeholder: boolean
}

export function getAgents(): Promise<AgentInfo[]> {
  return get<AgentInfo[]>('/api/v1/agents/')
}
