import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { TravelRequest, TravelPlan } from '@/types'
import { setStorage, removeStorage, STORAGE_KEYS } from '@/utils/storage'

interface TravelState {
  currentRequest: TravelRequest | null
  plans: TravelPlan[]
  selectedPlan: TravelPlan | null
}

interface TravelActions {
  setCurrentRequest: (request: TravelRequest) => void
  clearCurrentRequest: () => void
  setPlans: (plans: TravelPlan[]) => void
  addPlan: (plan: TravelPlan) => void
  selectPlan: (plan: TravelPlan) => void
  clearSelectedPlan: () => void
  clearAll: () => void
}

export type TravelStore = TravelState & TravelActions

export const useTravelStore = create<TravelStore>()(
  persist(
    (set) => ({
      // 初始状态
      currentRequest: null,
      plans: [],
      selectedPlan: null,

      // 设置当前旅游请求
      setCurrentRequest: (request) => {
        setStorage(STORAGE_KEYS.TRAVEL_REQUEST, request)
        set({ currentRequest: request })
      },

      // 清除当前旅游请求
      clearCurrentRequest: () => {
        removeStorage(STORAGE_KEYS.TRAVEL_REQUEST)
        set({ currentRequest: null })
      },

      // 设置旅游方案列表
      setPlans: (plans) => {
        set({ plans })
      },

      // 添加旅游方案
      addPlan: (plan) => {
        set((state) => ({
          plans: [...state.plans, plan],
        }))
      },

      // 选择旅游方案
      selectPlan: (plan) => {
        setStorage(STORAGE_KEYS.SELECTED_PLAN, plan)
        set({ selectedPlan: plan })
      },

      // 清除选中的旅游方案
      clearSelectedPlan: () => {
        removeStorage(STORAGE_KEYS.SELECTED_PLAN)
        set({ selectedPlan: null })
      },

      // 清除所有数据
      clearAll: () => {
        removeStorage(STORAGE_KEYS.TRAVEL_REQUEST)
        removeStorage(STORAGE_KEYS.SELECTED_PLAN)
        set({
          currentRequest: null,
          plans: [],
          selectedPlan: null,
        })
      },
    }),
    {
      name: 'travel-storage',
      partialize: (state) => ({
        currentRequest: state.currentRequest,
        selectedPlan: state.selectedPlan,
      }),
    }
  )
)
