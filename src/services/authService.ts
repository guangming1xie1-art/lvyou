import { http } from '@/utils/request'
import type { User, LoginRequest, RegisterRequest, AuthResponse } from '@/types'
import { API_ENDPOINTS } from './api'

/**
 * 认证服务
 */
export const authService = {
  /**
   * 用户登录
   */
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    return await http.post<AuthResponse>(API_ENDPOINTS.AUTH.LOGIN, credentials)
  },

  /**
   * 用户注册
   */
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    return await http.post<AuthResponse>(API_ENDPOINTS.AUTH.REGISTER, data)
  },

  /**
   * 用户登出
   */
  logout: async (): Promise<void> => {
    return await http.post<void>(API_ENDPOINTS.AUTH.LOGOUT)
  },

  /**
   * 刷新 token
   */
  refreshToken: async (): Promise<{ token: string }> => {
    return await http.post<{ token: string }>(API_ENDPOINTS.AUTH.REFRESH)
  },

  /**
   * 获取用户信息
   */
  getProfile: async (): Promise<User> => {
    return await http.get<User>(API_ENDPOINTS.AUTH.PROFILE)
  },

  /**
   * 更新用户信息
   */
  updateProfile: async (data: Partial<User>): Promise<User> => {
    return await http.put<User>(API_ENDPOINTS.AUTH.PROFILE, data)
  },
}
