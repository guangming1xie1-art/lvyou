import { useMutation, useState } from '@tanstack/react-query'
import { agentApiService } from '@/services/agentApi'
import type { RecommendRequest, RecommendResponse } from '@/types/api'

/**
 * 推荐相关的自定义 Hook
 * 管理旅行推荐的状态和操作
 */
export const useRecommend = () => {
  // 获取推荐
  const recommendMutation = useMutation({
    mutationFn: (params: RecommendRequest) => agentApiService.recommend(params),
  })

  return {
    // 数据
    data: recommendMutation.data,
    
    // 状态
    loading: recommendMutation.isPending,
    error: recommendMutation.error,
    
    // 操作方法
    recommend: recommendMutation.mutate,
    recommendAsync: recommendMutation.mutateAsync,
    
    // 辅助方法
    reset: recommendMutation.reset,
    
    // 状态标识
    isRecommending: recommendMutation.isPending,
    isSuccess: recommendMutation.isSuccess,
    isError: recommendMutation.isError,
    
    // 推荐结果
    recommendationResults: recommendMutation.data,
    destinationInfo: recommendMutation.data?.destination_info,
    attractions: recommendMutation.data?.attractions,
    weatherForecast: recommendMutation.data?.weather_forecast,
    reviews: recommendMutation.data?.reviews,
    taskId: recommendMutation.data?.task_id,
  }
}

/**
 * 简化的推荐 Hook，返回基本的状态
 */
export const useSimpleRecommend = () => {
  const [data, setData] = useState<RecommendResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const recommend = async (params: RecommendRequest) => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await agentApiService.recommend(params)
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取推荐失败'))
    } finally {
      setLoading(false)
    }
  }

  return {
    data,
    loading,
    error,
    recommend,
  }
}