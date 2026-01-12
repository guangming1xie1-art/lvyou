import { useQuery, useQueryClient } from '@tanstack/react-query'
import { agentApiService } from '@/services/agentApi'
import type { StatusResponse, TaskStatus } from '@/types/api'
import { useEffect, useRef, useState } from 'react'

// 轮询间隔配置
const POLLING_INTERVALS = {
  PENDING: 1000, // 1秒
  PROCESSING: 2000, // 2秒
  COMPLETED: 0, // 完成后停止轮询
  FAILED: 0, // 失败后停止轮询
}

/**
 * 任务状态追踪 Hook
 * 自动轮询任务状态直到完成
 */
export const useTaskStatus = (
  taskId: string | null,
  options: {
    enabled?: boolean
    initialStatus?: TaskStatus
    onComplete?: (data: StatusResponse) => void
    onError?: (error: Error) => void
    pollingEnabled?: boolean
  } = {}
) => {
  const {
    enabled = true,
    initialStatus = 'pending',
    onComplete,
    onError,
    pollingEnabled = true,
  } = options

  const [currentStatus, setCurrentStatus] = useState<TaskStatus>(initialStatus)
  const [progress, setProgress] = useState(0)
  const queryClient = useQueryClient()
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isPollingRef = useRef(false)

  // 查询任务状态
  const {
    data,
    error,
    isLoading,
    isError,
    isSuccess,
    refetch,
  } = useQuery<StatusResponse>({
    queryKey: ['task-status', taskId],
    queryFn: async () => {
      if (!taskId) throw new Error('Task ID is required')
      return await agentApiService.getStatus(taskId)
    },
    enabled: enabled && !!taskId,
    refetchOnMount: 'always',
    refetchOnWindowFocus: false,
    staleTime: 0, // 总是获取最新状态
    retry: false, // 不自动重试，由轮询控制
  })

  // 轮询逻辑
  const startPolling = () => {
    if (!taskId || !pollingEnabled || isPollingRef.current) return

    isPollingRef.current = true
    const poll = async () => {
      try {
        const result = await agentApiService.getStatus(taskId)
        
        // 更新状态
        setCurrentStatus(result.status)
        setProgress(result.progress)

        // 如果任务完成或失败，停止轮询
        if (result.status === 'completed') {
          isPollingRef.current = false
          onComplete?.(result)
          return
        }

        if (result.status === 'failed') {
          isPollingRef.current = false
          onError?.(new Error(result.error?.message || '任务执行失败'))
          return
        }

        // 继续轮询
        if (isPollingRef.current) {
          const interval = POLLING_INTERVALS[result.status] || 2000
          timeoutRef.current = setTimeout(poll, interval)
        }
      } catch (err) {
        isPollingRef.current = false
        onError?.(err instanceof Error ? err : new Error('获取任务状态失败'))
      }
    }

    // 开始轮询
    poll()
  }

  // 停止轮询
  const stopPolling = () => {
    isPollingRef.current = false
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
  }

  // 手动刷新状态
  const refreshStatus = () => {
    stopPolling()
    return refetch()
  }

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      stopPolling()
    }
  }, [])

  // 当 taskId 变化时重启轮询
  useEffect(() => {
    if (taskId && enabled && pollingEnabled) {
      stopPolling()
      setCurrentStatus('pending')
      setProgress(0)
      startPolling()
    } else {
      stopPolling()
    }
  }, [taskId, enabled, pollingEnabled])

  // 当状态变化时检查是否需要停止轮询
  useEffect(() => {
    if (data) {
      setCurrentStatus(data.status)
      setProgress(data.progress)

      if (data.status === 'completed' || data.status === 'failed') {
        stopPolling()
      }
    }
  }, [data])

  return {
    // 状态数据
    data,
    status: data?.status || currentStatus,
    progress: data?.progress ?? progress,
    result: data?.result,
    error: data?.error || error,
    
    // 状态标识
    isLoading,
    isError,
    isSuccess,
    isPending: data?.status === 'pending' || currentStatus === 'pending',
    isProcessing: data?.status === 'processing' || currentStatus === 'processing',
    isCompleted: data?.status === 'completed',
    isFailed: data?.status === 'failed',
    
    // 操作方法
    refetch: refreshStatus,
    startPolling,
    stopPolling,
  }
}

/**
 * 简化的任务状态 Hook，返回基本的状态
 */
export const useSimpleTaskStatus = (taskId: string | null) => {
  const [status, setStatus] = useState<TaskStatus>('pending')
  const [progress, setProgress] = useState(0)
  const [data, setData] = useState<StatusResponse | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(false)

  const checkStatus = async () => {
    if (!taskId) return
    
    setLoading(true)
    setError(null)
    
    try {
      const result = await agentApiService.getStatus(taskId)
      setData(result)
      setStatus(result.status)
      setProgress(result.progress)
      
      if (result.status === 'completed' || result.status === 'failed') {
        // 可以在这里停止轮询
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取状态失败'))
    } finally {
      setLoading(false)
    }
  }

  return {
    data,
    status,
    progress,
    error,
    loading,
    checkStatus,
  }
}