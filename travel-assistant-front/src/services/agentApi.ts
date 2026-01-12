/**
 * Agent API 服务层
 * 封装与后端 Agent REST API 的所有交互
 */

import { http } from '@/utils/request'
import { API_ENDPOINTS } from './api'
import type {
  SearchRequest,
  SearchResponse,
  RecommendRequest,
  RecommendResponse,
  BookRequest,
  BookResponse,
  StatusResponse,
  TaskListResponse,
  ApiConfig,
  ErrorDetail,
} from '@/types/api'

// API 配置
const DEFAULT_CONFIG: ApiConfig = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
  retries: 3,
}

// 错误处理工具函数
const handleApiError = (error: unknown): ErrorDetail => {
  if (error && typeof error === 'object' && 'code' in error && 'message' in error) {
    return error as ErrorDetail
  }
  
  return {
    code: 'UNKNOWN_ERROR',
    message: error instanceof Error ? error.message : '未知错误',
  }
}

// 重试机制
const withRetry = async <T>(
  operation: () => Promise<T>,
  retries: number = DEFAULT_CONFIG.retries,
  delay: number = 1000
): Promise<T> => {
  try {
    return await operation()
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, delay))
      return withRetry(operation, retries - 1, delay * 2)
    }
    throw error
  }
}

/**
 * Agent API 服务类
 */
export class AgentApiService {
  private config: ApiConfig

  constructor(config: Partial<ApiConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
  }

  /**
   * 搜索航班和酒店
   */
  async search(params: SearchRequest): Promise<SearchResponse> {
    return withRetry(async () => {
      return await http.post<SearchResponse>(API_ENDPOINTS.AGENT.SEARCH, params)
    })
  }

  /**
   * 获取旅行推荐
   */
  async recommend(params: RecommendRequest): Promise<RecommendResponse> {
    return withRetry(async () => {
      return await http.post<RecommendResponse>(API_ENDPOINTS.AGENT.RECOMMEND, params)
    })
  }

  /**
   * 创建预订
   */
  async book(params: BookRequest): Promise<BookResponse> {
    return withRetry(async () => {
      return await http.post<BookResponse>(API_ENDPOINTS.AGENT.BOOK, params)
    })
  }

  /**
   * 获取任务状态
   */
  async getStatus(taskId: string): Promise<StatusResponse> {
    return withRetry(async () => {
      return await http.get<StatusResponse>(API_ENDPOINTS.AGENT.TASK_STATUS(taskId))
    })
  }

  /**
   * 获取任务列表
   */
  async getTasks(params?: { status?: string; limit?: number }): Promise<TaskListResponse> {
    const queryParams = new URLSearchParams()
    if (params?.status) queryParams.append('status', params.status)
    if (params?.limit) queryParams.append('limit', params.limit.toString())

    const url = `${API_ENDPOINTS.AGENT.TASKS}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    
    return withRetry(async () => {
      return await http.get<TaskListResponse>(url)
    })
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await http.get<{ status: string; timestamp: string }>('/health')
      return response
    } catch (error) {
      return {
        status: 'error',
        timestamp: new Date().toISOString(),
      }
    }
  }
}

// 创建单例实例
export const agentApi = new AgentApiService()

// 导出便捷方法
export const agentApiService = {
  /**
   * 搜索服务
   */
  search: (params: SearchRequest) => agentApi.search(params),

  /**
   * 推荐服务
   */
  recommend: (params: RecommendRequest) => agentApi.recommend(params),

  /**
   * 预订服务
   */
  book: (params: BookRequest) => agentApi.book(params),

  /**
   * 状态查询服务
   */
  getStatus: (taskId: string) => agentApi.getStatus(taskId),

  /**
   * 任务列表服务
   */
  getTasks: (params?: { status?: string; limit?: number }) => agentApi.getTasks(params),

  /**
   * 健康检查
   */
  healthCheck: () => agentApi.healthCheck(),
}

export default agentApiService