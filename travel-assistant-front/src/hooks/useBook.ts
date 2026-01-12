import { useMutation, useState } from '@tanstack/react-query'
import { agentApiService } from '@/services/agentApi'
import type { BookRequest, BookResponse } from '@/types/api'

/**
 * 预订相关的自定义 Hook
 * 管理旅行预订的状态和操作
 */
export const useBook = () => {
  // 创建预订
  const bookMutation = useMutation({
    mutationFn: (params: BookRequest) => agentApiService.book(params),
  })

  return {
    // 数据
    data: bookMutation.data,
    
    // 状态
    loading: bookMutation.isPending,
    error: bookMutation.error,
    
    // 操作方法
    book: bookMutation.mutate,
    bookAsync: bookMutation.mutateAsync,
    
    // 辅助方法
    reset: bookMutation.reset,
    
    // 状态标识
    isBooking: bookMutation.isPending,
    isSuccess: bookMutation.isSuccess,
    isError: bookMutation.isError,
    
    // 预订结果
    bookingResults: bookMutation.data,
    bookingId: bookMutation.data?.booking_id,
    status: bookMutation.data?.status,
    confirmationNumber: bookMutation.data?.confirmation_number,
    priceBreakdown: bookMutation.data?.price_breakdown,
    tripSummary: bookMutation.data?.trip_summary,
    nextSteps: bookMutation.data?.next_steps,
    taskId: bookMutation.data?.task_id,
  }
}

/**
 * 简化的预订 Hook，返回基本的状态
 */
export const useSimpleBook = () => {
  const [data, setData] = useState<BookResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const book = async (params: BookRequest) => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await agentApiService.book(params)
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('预订失败'))
    } finally {
      setLoading(false)
    }
  }

  return {
    data,
    loading,
    error,
    book,
  }
}