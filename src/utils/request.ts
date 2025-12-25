import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import type { ApiResponse, ApiError } from '@/types'

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

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
  (error: AxiosError<ApiResponse<unknown>>) => {
    // 处理 HTTP 错误
    if (error.response) {
      const { status, data } = error.response

      // 处理特定的 HTTP 状态码
      switch (status) {
        case 401:
          // 未授权，清除 token 并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          break
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
