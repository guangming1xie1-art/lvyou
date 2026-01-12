import { useState, useCallback } from 'react'
import { RecommendRequest, RecommendResponse, ProgressMessage } from '../types/api'
import { webSocketAgentClient } from '../services/webSocketAgent'
import { useRecommend } from './useRecommend'

export const useWebSocketRecommend = () => {
  const [data, setData] = useState<RecommendResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<string>('')
  const { recommend: recommendHttp } = useRecommend()
  
  const recommend = useCallback(async (params: RecommendRequest) => {
    setLoading(true)
    setError(null)
    setProgress(0)
    setStatus('connecting')
    setData(null)

    try {
      try {
        webSocketAgentClient.onProgress((p: ProgressMessage) => {
          setProgress(p.progress)
          setStatus(p.message)
        })

        webSocketAgentClient.onIntermediateResult((partialData: any) => {
          setData(prev => ({
            ...prev,
            ...partialData
          } as RecommendResponse))
        })

        const result = await webSocketAgentClient.recommend(params)
        setData(result)
        setProgress(1)
        setStatus('completed')
      } catch (wsErr) {
        console.warn('WebSocket failed, falling back to HTTP:', wsErr)
        setStatus('falling_back')
        const result = await recommendHttp(params)
        setData(result as RecommendResponse)
        setProgress(1)
        setStatus('completed')
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Recommendation failed'))
      setStatus('failed')
    } finally {
      setLoading(false)
    }
  }, [recommendHttp])

  const cancel = useCallback(() => {
    webSocketAgentClient.cancel()
    setLoading(false)
    setStatus('cancelled')
  }, [])

  return {
    data,
    loading,
    error,
    progress,
    status,
    recommend,
    cancel
  }
}
