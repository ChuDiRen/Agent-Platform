/**
 * Unified API response types matching backend format
 * Backend standard: { code: number, message: string, data: T }
 */

/** Standard API response wrapper */
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

/** Paginated list response data */
export interface PaginatedData<T> {
  items: T[]
  total: number
}

/** Paginated API response (data contains items + total) */
export type PaginatedResponse<T> = ApiResponse<PaginatedData<T>>

/** Pagination query parameters */
export interface PageParams {
  page?: number
  page_size?: number
  skip?: number
  limit?: number
}

/** Common list query params extending pagination */
export interface ListParams extends PageParams {
  keyword?: string
  [key: string]: unknown
}

/** Standard success code */
export const API_SUCCESS_CODE = 0
