import { 
  SearchRequest, 
  SearchResponse, 
  RecommendRequest, 
  RecommendResponse, 
  BookRequest, 
  BookResponse,
  WSIncomingMessage,
  ProgressMessage,
  WSAction
} from '../types/api'

class WebSocketAgentClient {
  private ws: WebSocket | null = null
  private url: string
  private onProgressCallback: ((progress: ProgressMessage) => void) | null = null
  private onIntermediateResultCallback: ((data: any) => void) | null = null
  private currentResolve: ((value: any) => void) | null = null
  private currentReject: ((reason: any) => void) | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = Number(import.meta.env.VITE_WS_MAX_RETRIES || 3)
  private heartbeatInterval: number | null = null

  constructor(url: string = import.meta.env.VITE_AGENT_WS_URL || 'ws://localhost:8000/ws/agent/stream') {
    this.url = url
  }

  private connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          const message: WSIncomingMessage = JSON.parse(event.data)
          this.handleMessage(message)
        }

        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.stopHeartbeat()
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            setTimeout(() => this.connect(), 1000 * this.reconnectAttempts)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private handleMessage(message: WSIncomingMessage) {
    switch (message.type) {
      case 'progress':
        this.onProgressCallback?.(message)
        break
      case 'intermediate':
        this.onIntermediateResultCallback?.(message.data)
        break
      case 'complete':
        this.currentResolve?.(message.data)
        this.clearPendingRequest()
        break
      case 'error':
        this.currentReject?.(new Error(message.error))
        this.clearPendingRequest()
        break
    }
  }

  private clearPendingRequest() {
    this.currentResolve = null
    this.currentReject = null
  }

  private startHeartbeat() {
    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: 'heartbeat' }))
      }
    }, Number(import.meta.env.VITE_WS_HEARTBEAT_INTERVAL || 30000))
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  async search(params: SearchRequest): Promise<SearchResponse> {
    await this.connect()
    return new Promise((resolve, reject) => {
      this.currentResolve = resolve
      this.currentReject = reject
      this.ws?.send(JSON.stringify({
        action: 'search',
        params
      }))
    })
  }

  async recommend(params: RecommendRequest): Promise<RecommendResponse> {
    await this.connect()
    return new Promise((resolve, reject) => {
      this.currentResolve = resolve
      this.currentReject = reject
      this.ws?.send(JSON.stringify({
        action: 'recommend',
        params
      }))
    })
  }

  async book(params: BookRequest): Promise<BookResponse> {
    await this.connect()
    return new Promise((resolve, reject) => {
      this.currentResolve = resolve
      this.currentReject = reject
      this.ws?.send(JSON.stringify({
        action: 'book',
        params
      }))
    })
  }

  onProgress(callback: (progress: ProgressMessage) => void) {
    this.onProgressCallback = callback
  }

  onIntermediateResult(callback: (data: any) => void) {
    this.onIntermediateResultCallback = callback
  }

  cancel() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.clearPendingRequest()
  }
}

export const webSocketAgentClient = new WebSocketAgentClient()
export default WebSocketAgentClient
