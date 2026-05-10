import { post, get } from './http'

export interface LoginRequest {
  email: string
  password: string
}

export interface UserInfo {
  id: number
  email: string
  full_name: string
  is_active: boolean
  is_superuser: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export function login(data: LoginRequest): Promise<LoginResponse> {
  return post<LoginResponse>('/api/v1/users/login', data)
}

export function getUserInfo(userId: number): Promise<UserInfo> {
  return get<UserInfo>(`/api/v1/users/${userId}`)
}

export function getUsers(skip = 0, limit = 100): Promise<UserInfo[]> {
  return get<UserInfo[]>('/api/v1/users/', { skip, limit })
}
