export interface ProjectCreate {
  name: string
  description?: string
  password?: string
  llm_url?: string
  llm_key?: string
  llm_model?: string
  lvm_url?: string
  lvm_key?: string
  lvm_model?: string
  extend_json?: string
}

export interface ProjectUpdate {
  name?: string
  description?: string
  password?: string
  llm_url?: string
  llm_key?: string
  llm_model?: string
  lvm_url?: string
  lvm_key?: string
  lvm_model?: string
  extend_json?: string
}

export interface ProjectInfo {
  id: number
  name: string
  description?: string
  password?: string
  llm_url?: string
  llm_key?: string
  llm_model?: string
  lvm_url?: string
  lvm_key?: string
  lvm_model?: string
  created_at?: string
  updated_at?: string
  extend_json?: string
}
