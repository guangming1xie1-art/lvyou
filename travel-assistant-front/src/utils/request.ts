import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { authService } from '@/services/authService'
import type { ApiResponse, ApiError } from '@/types'

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 注入 JWT token
request.interceptors.request.use(
  async (config) => {
    try {
      // 从 auth service 获取有效的 access token
      const token = await authService.getValidToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    } catch (error) {
      // Token 无效，继续请求，由响应拦截器处理 401
      console.debug('Token not available for request:', config.url)
    }
    return config
  },
  (error: AxiosError) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理 401 和 token 刷新
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: any) => void
}>[] = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else if (token) {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse<unknown>>) => {
    const { data } = response

    // 检查业务状态码
    if (data.code !== 200 && data.code !== 0) {
      const error: ApiError = {
        code: data.code,
        message: data.message || '请求失败',
      }
      return Promise.reject(error)
    }

    return response
  },
  async (error: AxiosError<ApiResponse<unknown>>) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean; _queued?: boolean }

    // 处理 401 未授权错误
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // 如果正在刷新，将请求加入队列
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            return request(originalRequest)
          })
          .catch(err => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // 尝试刷新 token
        await authService.refreshToken()
        const newToken = authService.getAccessToken()

        // 处理队列中的请求
        processQueue(null, newToken || '')

        // 重试原始请求
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`
        }
        return request(originalRequest)
      } catch (refreshError) {
        // 刷新失败，清除认证状态并跳转登录
        processQueue(refreshError, null)
        authService.clearTokens?.()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // 处理其他 HTTP 错误
    if (error.response) {
      const { status, data } = error.response

      // 处理特定的 HTTP 状态码
      switch (status) {
        case 403:
          console.error('无权限访问')
          break
        case 404:
          console.error('请求的资源不存在')
          break
        case 500:
          console.error('服务器错误')
          break
        default:
          console.error('请求失败')
      }

      const apiError: ApiError = {
        code: data?.code || status,
        message: data?.message || '请求失败',
        details: data,
      }
      return Promise.reject(apiError)
    }

    // 网络错误
    if (error.message === 'Network Error') {
      console.error('网络连接失败')
    } else if (error.code === 'ECONNABORTED') {
      console.error('请求超时')
    }

    return Promise.reject(error)
  }
)

// 封装常用的请求方法
export const http = {
  get: <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return request.get<ApiResponse<T>>(url, config).then((res) => res.data.data as T)
  },

  post: <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    return request.post<ApiResponse<T>>(url, data, config).then((res) => res.data.data as T)
  },

  put: <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    return request.put<ApiResponse<T>>(url, data, config).then((res) => res.data.data as T)
  },

  delete: <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return request.delete<ApiResponse<T>>(url, config).then((res) => res.data.data as T)
  },

  patch: <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    return request.patch<ApiResponse<T>>(url, data, config).then((res) => res.data.data as T)
  },
}

export default request
