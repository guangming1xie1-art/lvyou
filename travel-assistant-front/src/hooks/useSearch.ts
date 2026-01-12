import { useMutation, useState } from '@tanstack/react-query'
import { agentApiService } from '@/services/agentApi'
import type { SearchRequest, SearchResponse } from '@/types/api'

/**
 * 搜索相关的自定义 Hook
 * 管理航班和酒店搜索的状态和操作
 */
export const useSearch = () => {
  // 搜索航班和酒店
  const searchMutation = useMutation({
    mutationFn: (params: SearchRequest) => agentApiService.search(params),
  })

  return {
    // 数据
    data: searchMutation.data,
    
    // 状态
    loading: searchMutation.isPending,
    error: searchMutation.error,
    
    // 操作方法
    search: searchMutation.mutate,
    searchAsync: searchMutation.mutateAsync,
    
    // 辅助方法
    reset: searchMutation.reset,
    
    // 状态标识
    isSearching: searchMutation.isPending,
    isSuccess: searchMutation.isSuccess,
    isError: searchMutation.isError,
    
    // 搜索结果
    searchResults: searchMutation.data,
    outboundFlights: searchMutation.data?.outbound_flights,
    returnFlights: searchMutation.data?.return_flights,
    hotels: searchMutation.data?.hotels,
    searchMetadata: searchMutation.data?.search_metadata,
    taskId: searchMutation.data?.task_id,
  }
}

/**
 * 简化的搜索 Hook，返回基本的状态
 */
export const useSimpleSearch = () => {
  const [data, setData] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const search = async (params: SearchRequest) => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await agentApiService.search(params)
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('搜索失败'))
    } finally {
      setLoading(false)
    }
  }

  return {
    data,
    loading,
    error,
    search,
  }
}