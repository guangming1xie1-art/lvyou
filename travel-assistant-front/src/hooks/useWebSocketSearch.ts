import { useState, useCallback } from 'react'
import { SearchRequest, SearchResponse, ProgressMessage } from '../types/api'
import { webSocketAgentClient } from '../services/webSocketAgent'
import { useSearch } from './useSearch'

export const useWebSocketSearch = () => {
  const [data, setData] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<string>('')
  const { search: searchHttp } = useSearch()
  
  const search = useCallback(async (params: SearchRequest) => {
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
          } as SearchResponse))
        })

        const result = await webSocketAgentClient.search(params)
        setData(result)
        setProgress(1)
        setStatus('completed')
      } catch (wsErr) {
        console.warn('WebSocket failed, falling back to HTTP:', wsErr)
        setStatus('falling_back')
        const result = await searchHttp(params)
        setData(result as SearchResponse)
        setProgress(1)
        setStatus('completed')
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Search failed'))
      setStatus('failed')
    } finally {
      setLoading(false)
    }
  }, [searchHttp])

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
    search,
    cancel
  }
}
