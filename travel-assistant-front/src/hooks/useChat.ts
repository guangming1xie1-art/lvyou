import { useMutation } from '@tanstack/react-query'
import { agentApiService } from '@/services/agentApi'
import type { ConversationResponse } from '@/types/chat'

export function useChat() {
  return useMutation<ConversationResponse, Error, string>({
    mutationFn: (message: string) => agentApiService.chat(message),
  })
}
