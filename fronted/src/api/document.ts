import { del, get, post, put } from './http'
import type { AgentTask } from './agentTask'
import { getPageItems, type PaginatedData } from './pagination'

export type FindingSeverity = 'high' | 'medium' | 'low'

export interface RequirementFinding {
  id: string
  title: string
  description: string
  severity: FindingSeverity
  category: string
  adopted: boolean
}

export interface RequirementDocument {
  id: number
  project_id?: number | null
  name: string
  parent_id?: number | null
  title?: string | null
  content?: string | null
  created_by?: string | null
  is_directory: boolean
  ai_suggest: RequirementFinding[]
  created_at?: string | null
  updated_at?: string | null
}

export interface DocumentPayload {
  project_id?: number | null
  name: string
  parent_id?: number | null
  title?: string | null
  content?: string | null
  created_by?: string | null
  is_directory?: boolean
  ai_suggest?: RequirementFinding[]
}

export interface RequirementReviewRequest {
  document_id?: number
  title?: string | null
  content: string
  extra_prompt?: string
}

export interface RequirementReviewResponse {
  document_id?: number | null
  title?: string | null
  findings: RequirementFinding[]
}

export function getDocuments(projectId?: number): Promise<RequirementDocument[]> {
  return get<PaginatedData<RequirementDocument>>(
    '/api/v1/documents/',
    projectId ? { project_id: projectId } : undefined,
  ).then(getPageItems)
}

export function createDocument(data: DocumentPayload): Promise<RequirementDocument> {
  return post<RequirementDocument>('/api/v1/documents/', data)
}

export function updateDocument(
  documentId: number,
  data: Partial<DocumentPayload>,
): Promise<RequirementDocument> {
  return put<RequirementDocument>(`/api/v1/documents/${documentId}`, data)
}

export function deleteDocument(documentId: number): Promise<RequirementDocument> {
  return del<RequirementDocument>(`/api/v1/documents/${documentId}`)
}

export function reviewRequirement(
  data: RequirementReviewRequest,
): Promise<AgentTask<RequirementReviewResponse>> {
  return post<AgentTask<RequirementReviewResponse>>('/api/v1/documents/review', data)
}
