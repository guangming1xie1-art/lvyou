import type { ConversationResponse } from '@/types/chat'
import type {
  BookRequest,
  BookResponse,
  RecommendRequest,
  RecommendResponse,
  SearchRequest,
  SearchResponse,
  StatusResponse,
  TaskListResponse,
} from '@/types/api'
import { authService } from '@/services/authService'

const AGENT_BASE_URL = import.meta.env.VITE_AGENT_API_BASE_URL || 'http://localhost:8000'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

async function request<T>(method: HttpMethod, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  try {
    const token = await authService.getValidToken()
    if (token) headers.Authorization = `Bearer ${token}`
  } catch {
    // no-op: request may be public or will fail with 401
  }

  const resp = await fetch(`${AGENT_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  const text = await resp.text()
  const json = text ? (JSON.parse(text) as any) : null

  if (!resp.ok) {
    const detail = json?.detail || json?.message || resp.statusText
    throw new Error(typeof detail === 'string' ? detail : 'Request failed')
  }

  // Support both raw response and {code,message,data} wrapper
  return (json?.data ?? json) as T
}

export class AgentApiService {
  static async chat(message: string): Promise<ConversationResponse> {
    return request<ConversationResponse>('POST', '/chat', { message })
  }

  static async search(params: SearchRequest): Promise<SearchResponse> {
    return request<SearchResponse>('POST', '/api/agent/search', params)
  }

  static async recommend(params: RecommendRequest): Promise<RecommendResponse> {
    return request<RecommendResponse>('POST', '/api/agent/recommend', params)
  }

  static async book(params: BookRequest): Promise<BookResponse> {
    return request<BookResponse>('POST', '/api/agent/book', params)
  }

  static async getStatus(taskId: string): Promise<StatusResponse> {
    return request<StatusResponse>('GET', `/api/agent/status/${taskId}`)
  }

  static async getTasks(): Promise<TaskListResponse> {
    return request<TaskListResponse>('GET', '/api/agent/tasks')
  }

  static async healthCheck(): Promise<{ status: string }>
  static async healthCheck(): Promise<{ status: string }> {
    const data = await request<any>('GET', '/api/agent/status')
    return { status: data?.status || 'ok' }
  }
}

export const agentApiService = AgentApiService

export default agentApiService
