export type ChatRole = 'user' | 'assistant'

export interface ConversationResponse {
  search_results: Array<Record<string, any>>
  recommendations: Array<Record<string, any>>
  booking_info: Record<string, any>
  response: string
  status: string
  error?: string
}

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  data?: ConversationResponse
  timestamp: number
}
