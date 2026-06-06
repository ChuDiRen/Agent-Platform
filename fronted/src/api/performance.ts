import { del, get, post } from './http'

export interface PerformanceMetric {
  name: string
  value: number
  unit: string
  threshold?: number | null
}

export interface PerformanceFinding {
  title: string
  severity: string
  description: string
  suggestion: string
}

export interface PerformanceAnalysis {
  score: number
  summary: string
  findings: PerformanceFinding[]
  trends: string[]
}

export interface PerformanceConfigs {
  name: string
  source: string
  scenario: string
  raw_text: string
  metrics: PerformanceMetric[]
  analysis?: PerformanceAnalysis | null
}

export interface PerformanceRecord {
  id: number
  project_id?: number | null
  configs: PerformanceConfigs
  created_at?: string | null
  updated_at?: string | null
}

export interface PerformanceAnalyzeRequest {
  project_id?: number | null
  name: string
  scenario: string
  raw_text: string
  metrics?: PerformanceMetric[]
}

export interface PerformanceAnalyzeResponse {
  record: PerformanceRecord
  analysis: PerformanceAnalysis
  elapsed_ms: number
}

export function analyzePerformance(data: PerformanceAnalyzeRequest): Promise<PerformanceAnalyzeResponse> {
  return post<PerformanceAnalyzeResponse>('/api/v1/performance/analyze', data)
}

export function getPerformanceRecords(projectId?: number): Promise<PerformanceRecord[]> {
  return get<PerformanceRecord[]>('/api/v1/performance/', projectId ? { project_id: projectId } : undefined)
}

export function getPerformanceRecord(recordId: number): Promise<PerformanceRecord> {
  return get<PerformanceRecord>(`/api/v1/performance/${recordId}`)
}

export function deletePerformanceRecord(recordId: number): Promise<PerformanceRecord> {
  return del<PerformanceRecord>(`/api/v1/performance/${recordId}`)
}
