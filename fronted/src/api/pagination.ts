export interface PaginatedData<T> {
  items: T[]
  total: number
  page?: number
  page_size?: number
}

export function getPageItems<T>(data: PaginatedData<T>): T[] {
  return data.items
}
