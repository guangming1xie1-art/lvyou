import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { authService } from '@/services/authService'
import type { LoginRequest, RegisterRequest } from '@/types'

/**
 * 认证相关的自定义 Hook
 */
export const useAuth = () => {
  const navigate = useNavigate()
  const { user, token, isAuthenticated, login, logout, setUser } = useAuthStore()

  // 登录
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginRequest) => authService.login(credentials),
    onSuccess: (data) => {
      login(data.user, data.token)
      navigate('/')
    },
  })

  // 注册
  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
    onSuccess: (data) => {
      login(data.user, data.token)
      navigate('/')
    },
  })

  // 登出
  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      logout()
      navigate('/login')
    },
  })

  // 获取用户信息
  const { data: profile, refetch: refetchProfile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => authService.getProfile(),
    enabled: isAuthenticated && !!token,
    staleTime: 1000 * 60 * 5, // 5分钟
  })

  // 更新用户信息
  const updateProfileMutation = useMutation({
    mutationFn: (data: Parameters<typeof authService.updateProfile>[0]) =>
      authService.updateProfile(data),
    onSuccess: (data) => {
      setUser(data)
      refetchProfile()
    },
  })

  return {
    user,
    token,
    isAuthenticated,
    profile,
    login: loginMutation.mutate,
    loginAsync: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    register: registerMutation.mutate,
    registerAsync: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error,
    logout: logoutMutation.mutate,
    isLoggingOut: logoutMutation.isPending,
    updateProfile: updateProfileMutation.mutate,
    updateProfileAsync: updateProfileMutation.mutateAsync,
    isUpdatingProfile: updateProfileMutation.isPending,
    refetchProfile,
  }
}
