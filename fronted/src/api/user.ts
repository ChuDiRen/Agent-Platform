import { post } from './http'

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

export interface UserUpdateRequest {
  email?: string
  full_name?: string
  password?: string
  is_active?: boolean
}

export function login(data: LoginRequest): Promise<LoginResponse> {
  return post<LoginResponse>('/api/v1/users/login', data)
}

export function register(data: {
  email: string
  password: string
  full_name?: string
}): Promise<UserInfo> {
  return post<UserInfo>('/api/v1/users/', data)
}
