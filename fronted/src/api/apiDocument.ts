import { del, get, post, put } from './http'
import type { AgentTask } from './agentTask'
import { getPageItems, type PaginatedData } from './pagination'

export type ApiFindingSeverity = 'high' | 'medium' | 'low'

export interface ApiDocumentFinding {
  id: string
  title: string
  description: string
  severity: ApiFindingSeverity
  category: string
  adopted: boolean
}

export interface ApiDocument {
  id: number
  project_id?: number | null
  name: string
  parent_id?: number | null
  title?: string | null
  content?: string | null
  created_by?: string | null
  is_directory: boolean
  ai_suggest: ApiDocumentFinding[]
  created_at?: string | null
  updated_at?: string | null
}

export interface ApiDocumentPayload {
  project_id?: number | null
  name: string
  parent_id?: number | null
  title?: string | null
  content?: string | null
  created_by?: string | null
  is_directory?: boolean
  ai_suggest?: ApiDocumentFinding[]
}

export interface ApiDocumentAnalysisRequest {
  document_id?: number
  title?: string | null
  content: string
  extra_prompt?: string
}

export interface ApiDocumentAnalysisResponse {
  document_id?: number | null
  title?: string | null
  findings: ApiDocumentFinding[]
}

export function getApiDocuments(projectId?: number): Promise<ApiDocument[]> {
  return get<PaginatedData<ApiDocument>>(
    '/api/v1/api-documents/',
    projectId ? { project_id: projectId } : undefined,
  ).then(getPageItems)
}

export function createApiDocument(data: ApiDocumentPayload): Promise<ApiDocument> {
  return post<ApiDocument>('/api/v1/api-documents/', data)
}

export function updateApiDocument(
  documentId: number,
  data: Partial<ApiDocumentPayload>,
): Promise<ApiDocument> {
  return put<ApiDocument>(`/api/v1/api-documents/${documentId}`, data)
}

export function deleteApiDocument(documentId: number): Promise<ApiDocument> {
  return del<ApiDocument>(`/api/v1/api-documents/${documentId}`)
}

export function analyzeApiDocument(
  data: ApiDocumentAnalysisRequest,
): Promise<AgentTask<ApiDocumentAnalysisResponse>> {
  return post<AgentTask<ApiDocumentAnalysisResponse>>('/api/v1/api-documents/analysis', data)
}
