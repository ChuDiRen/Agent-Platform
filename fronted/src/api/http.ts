import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import NProgress from '@/utils/nprogress'
import { baseUrl } from './baseUrl'

const service = axios.create({
  baseURL: baseUrl,
  timeout: 15000,
})

service.interceptors.request.use(
  (config) => {
    NProgress.start()
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = token
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

service.interceptors.response.use(
  (response: AxiosResponse) => {
    NProgress.done()
    if (response.status === 200) {
      return response.data
    }
    ElMessage.error(response.data?.message || '请求失败')
    return Promise.reject(new Error('请求失败'))
  },
  (error) => {
    NProgress.done()
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(error.message || '网络异常')
    }
    return Promise.reject(error)
  },
)

export function get<T>(url: string, params?: object, config?: AxiosRequestConfig): Promise<T> {
  return service.get(url, { params, ...config }) as Promise<T>
}

export function post<T>(url: string, data?: object, config?: AxiosRequestConfig): Promise<T> {
  return service.post(url, data, config) as Promise<T>
}

export function upload<T>(url: string, formData: FormData): Promise<T> {
  return service.post(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }) as Promise<T>
}

export function download(url: string, params?: object) {
  const iframe = document.createElement('iframe')
  iframe.src = `${baseUrl}${url}?${new URLSearchParams(params as Record<string, string>)}`
  iframe.style.display = 'none'
  document.body.appendChild(iframe)
  setTimeout(() => document.body.removeChild(iframe), 5000)
}

export default service
