import { get, post, put, del } from './http'
import type { ProjectCreate, ProjectUpdate, ProjectInfo } from './modules/project'

export type { ProjectCreate, ProjectUpdate, ProjectInfo }

export function createProject(data: ProjectCreate): Promise<ProjectInfo> {
  return post<ProjectInfo>('/api/v1/projects/', data)
}

export function getProject(projectId: number): Promise<ProjectInfo> {
  return get<ProjectInfo>(`/api/v1/projects/${projectId}`)
}

export function getProjects(skip = 0, limit = 100): Promise<ProjectInfo[]> {
  return get<ProjectInfo[]>('/api/v1/projects/', { skip, limit })
}

export function updateProject(projectId: number, data: ProjectUpdate): Promise<ProjectInfo> {
  return put<ProjectInfo>(`/api/v1/projects/${projectId}`, data)
}

export function deleteProject(projectId: number): Promise<ProjectInfo> {
  return del<ProjectInfo>(`/api/v1/projects/${projectId}`)
}
