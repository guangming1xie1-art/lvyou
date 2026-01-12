import { useState, useCallback } from 'react'
import { BookRequest, BookResponse, ProgressMessage } from '../types/api'
import { webSocketAgentClient } from '../services/webSocketAgent'
import { useBook } from './useBook'

export const useWebSocketBook = () => {
  const [data, setData] = useState<BookResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<string>('')
  const { book: bookHttp } = useBook()
  
  const book = useCallback(async (params: BookRequest) => {
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

        const result = await webSocketAgentClient.book(params)
        setData(result)
        setProgress(1)
        setStatus('completed')
      } catch (wsErr) {
        console.warn('WebSocket failed, falling back to HTTP:', wsErr)
        setStatus('falling_back')
        const result = await bookHttp(params)
        setData(result as BookResponse)
        setProgress(1)
        setStatus('completed')
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Booking failed'))
      setStatus('failed')
    } finally {
      setLoading(false)
    }
  }, [bookHttp])

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
    book,
    cancel
  }
}
