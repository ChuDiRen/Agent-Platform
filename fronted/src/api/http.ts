import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { ref } from 'vue'
import router from '@/router'
import { getToken, removeToken } from '@/utils/auth'
import { useUserStore } from '@/store/store'
import NProgress from '@/utils/nprogress'
import { baseUrl } from './baseUrl'
import { API_SUCCESS_CODE } from '@/types/api'

// ---------------------------------------------------------------------------
// Loading state management
// ---------------------------------------------------------------------------
const pendingCount = ref(0)

/** 是否有请求正在进行 */
export const isLoading = ref(false)

function incLoading() {
  pendingCount.value++
  isLoading.value = true
}

function decLoading() {
  pendingCount.value = Math.max(0, pendingCount.value - 1)
  if (pendingCount.value === 0) {
    isLoading.value = false
  }
}

function buildLoginRedirect() {
  const current = router.currentRoute.value
  const fullPath = current.fullPath || current.path
  return `/login?redirect=${encodeURIComponent(fullPath)}`
}

function handleUnauthorized() {
  removeToken()
  useUserStore().resetUser()
  const currentPath = router.currentRoute.value.path
  if (!['/login', '/register'].includes(currentPath)) {
    router.replace(buildLoginRedirect())
  }
}

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------
const service = axios.create({
  baseURL: baseUrl,
  timeout: 15000,
})

// ---------------------------------------------------------------------------
// Request interceptor
// ---------------------------------------------------------------------------
service.interceptors.request.use(
  (config) => {
    NProgress.start()
    incLoading()
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    decLoading()
    return Promise.reject(error)
  },
)

// ---------------------------------------------------------------------------
// Response interceptor
// 所有接口必须返回统一格式: { code: number, message: string, data: T }
// ---------------------------------------------------------------------------
service.interceptors.response.use(
  (response: AxiosResponse) => {
    NProgress.done()
    decLoading()

    if (response.status !== 200) {
      ElMessage.error(response.data?.message || '请求失败')
      return Promise.reject(new Error('请求失败'))
    }

    const body = response.data

    // 统一响应格式校验
    if (body.code === API_SUCCESS_CODE) {
      return body.data
    }

    // 业务错误
    ElMessage.error(body.message || '请求失败')
    return Promise.reject(new Error(body.message || '请求失败'))
  },
  (error) => {
    NProgress.done()
    decLoading()

    const status = error.response?.status
    if (status === 401) {
      handleUnauthorized()
      ElMessage.error('登录已过期，请重新登录')
    } else if (status === 403) {
      ElMessage.error('没有权限访问')
    } else if (status === 500) {
      ElMessage.error('服务器内部错误')
    } else {
      ElMessage.error(error.message || '网络异常')
    }
    return Promise.reject(error)
  },
)

// ---------------------------------------------------------------------------
// Public request helpers
// ---------------------------------------------------------------------------

export function get<T>(url: string, params?: object, config?: AxiosRequestConfig): Promise<T> {
  return service.get(url, { params, ...config }) as Promise<T>
}

export function post<T>(url: string, data?: object, config?: AxiosRequestConfig): Promise<T> {
  return service.post(url, data, config) as Promise<T>
}

export function put<T>(url: string, data?: object, config?: AxiosRequestConfig): Promise<T> {
  return service.put(url, data, config) as Promise<T>
}

export function del<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return service.delete(url, config) as Promise<T>
}

export function upload<T>(url: string, formData: FormData): Promise<T> {
  return service.post(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }) as Promise<T>
}

export function download(url: string, params?: object) {
  // 通过带 Authorization 的 axios 请求下载（iframe 直连无法携带 token，必然 401）
  const query = params ? `?${new URLSearchParams(params as Record<string, string>)}` : ''
  return service.get(`${url}${query}`, { responseType: 'blob' }).then((response) => {
    const disposition = response.headers['content-disposition'] || ''
    const match = disposition.match(/filename="?([^";]+)"?/)
    const filename = match ? match[1] : `download-${Date.now()}`
    const blobUrl = URL.createObjectURL(response.data as Blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = decodeURIComponent(filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(blobUrl)
    return response.data
  })
}

export { service }
export default service
