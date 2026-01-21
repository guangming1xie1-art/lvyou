import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChatInput } from '@/components/ChatInput'
import { Message } from '@/components/Message'
import { useChat } from '@/hooks/useChat'
import { useAuthStore } from '@/store'
import type { ChatMessage } from '@/types/chat'

const createId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="max-w-[92%] md:max-w-[70%] rounded-3xl border border-gray-200 bg-white/90 px-4 py-3 shadow-sm">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span className="text-base">🤖</span>
          <span>正在生成方案…</span>
        </div>
        <div className="mt-3 flex items-center gap-2">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="h-2 w-2 rounded-full bg-indigo-400 animate-bounce"
              style={{ animationDelay: `${i * 120}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    {
      id: createId(),
      role: 'assistant',
      content:
        '把你的旅行想法告诉我，我会为你一站式完成：\n\n1) 搜索（机票 / 酒店 / 景点等）\n2) 生成推荐行程与对比方案\n3) 如需要，提供预订信息与下一步建议\n\n你可以从「目的地、日期、天数、人数、预算、偏好」开始描述。',
      timestamp: Date.now(),
    },
  ])
  const [input, setInput] = useState('')

  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const { mutateAsync: sendMessage, isPending } = useChat()

  const scrollRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, isPending])

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
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-white to-indigo-50">
      <div className="border-b border-indigo-100 bg-white/70 backdrop-blur">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between py-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-sm shadow-indigo-200/60">
                🌍
              </div>
              <div>
                <div className="text-lg font-semibold leading-none text-gray-900">旅游助手</div>
                <div className="mt-1 text-xs text-gray-500">搜索 · 推荐 · 预订，一次性搞定</div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <span className="hidden sm:inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                在线
              </span>
              {user && <span className="hidden md:inline text-sm text-gray-700">欢迎，{user.name}</span>}
              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-2 rounded-xl border border-indigo-100 bg-white px-3 py-2 text-sm font-medium text-indigo-700 hover:bg-indigo-50 hover:border-indigo-200 transition-colors"
              >
                退出
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1">
        <div className="container mx-auto px-4 py-6">
          <div className="mx-auto max-w-4xl space-y-5 pb-28">
            {messages.map((msg, index) => (
              <Message key={msg.id} message={msg} isWelcome={index === 0 && msg.role === 'assistant' && !msg.data} />
            ))}

            {isPending && <TypingIndicator />}

            <div ref={scrollRef} />
          </div>
        </div>
      </div>

      <ChatInput value={input} onChange={setInput} onSend={handleSend} disabled={isPending} />
    </div>
  )
}
