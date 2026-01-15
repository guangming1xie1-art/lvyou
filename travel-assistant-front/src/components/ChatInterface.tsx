import { useEffect, useRef, useState } from 'react'
import { ChatInput } from '@/components/ChatInput'
import { Message } from '@/components/Message'
import { useChat } from '@/hooks/useChat'
import type { ChatMessage } from '@/types/chat'

const createId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    {
      id: createId(),
      role: 'assistant',
      content: '告诉我你的旅行需求，我会一次性给出搜索、推荐以及（如需要）预订信息。',
      timestamp: Date.now(),
    },
  ])
  const [input, setInput] = useState('')

  const { mutateAsync: sendMessage, isPending } = useChat()

  const scrollRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || isPending) return

    setInput('')

    const userMsg: ChatMessage = {
      id: createId(),
      role: 'user',
      content: text,
      timestamp: Date.now(),
    }
    setMessages((prev) => [...prev, userMsg])

    try {
      const data = await sendMessage(text)
      const assistantMsg: ChatMessage = {
        id: createId(),
        role: 'assistant',
        content: data.response || '已收到，我正在为你生成规划结果。',
        data,
        timestamp: Date.now(),
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (e) {
      const errorText = e instanceof Error ? e.message : '发送失败'
      setMessages((prev) => [
        ...prev,
        {
          id: createId(),
          role: 'assistant',
          content: `请求失败：${errorText}`,
          timestamp: Date.now(),
        },
      ])
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col bg-gray-50">
      <div className="flex-1">
        <div className="container mx-auto px-4 py-6 space-y-4">
          {messages.map((msg) => (
            <Message key={msg.id} message={msg} />
          ))}
          <div ref={scrollRef} />
        </div>
      </div>

      <ChatInput value={input} onChange={setInput} onSend={handleSend} disabled={isPending} />
    </div>
  )
}
