import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { setStorage, removeStorage, STORAGE_KEYS } from '@/utils/storage'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

interface AuthActions {
  setUser: (user: User) => void
  setToken: (token: string) => void
  login: (user: User, token: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
}

export type AuthStore = AuthState & AuthActions

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      // 初始状态
      user: null,
      token: null,
      isAuthenticated: false,

      // 设置用户信息
      setUser: (user) => {
        setStorage(STORAGE_KEYS.USER, user)
        set({ user, isAuthenticated: true })
      },

      // 设置 token
      setToken: (token) => {
        setStorage(STORAGE_KEYS.TOKEN, token)
        set({ token })
      },

      // 登录
      login: (user, token) => {
        setStorage(STORAGE_KEYS.USER, user)
        setStorage(STORAGE_KEYS.TOKEN, token)
        set({ user, token, isAuthenticated: true })
      },

      // 登出
      logout: () => {
        removeStorage(STORAGE_KEYS.USER)
        removeStorage(STORAGE_KEYS.TOKEN)
        set({ user: null, token: null, isAuthenticated: false })
      },

      // 更新用户信息
      updateUser: (userData) => {
        set((state) => {
          if (!state.user) return state
          const updatedUser = { ...state.user, ...userData }
          setStorage(STORAGE_KEYS.USER, updatedUser)
          return { user: updatedUser }
        })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
