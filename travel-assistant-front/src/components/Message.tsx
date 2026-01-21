import { useEffect, useMemo, useState } from 'react'
import type { ChatMessage } from '@/types/chat'
import { formatDate } from '@/utils/format'
import { JsonViewer } from '@/components/common/JsonViewer'

interface MessageProps {
  message: ChatMessage
  isWelcome?: boolean
}

function DataPanel({
  title,
  icon,
  count,
  value,
}: {
  title: string
  icon: React.ReactNode
  count?: number
  value: unknown
}) {
  return (
    <details className="rounded-2xl border border-indigo-100 bg-indigo-50/40 shadow-sm">
      <summary className="cursor-pointer list-none px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-base">{icon}</span>
          <span className="text-sm font-semibold text-gray-900">{title}</span>
          {typeof count === 'number' && (
            <span className="ml-auto rounded-full border border-indigo-100 bg-white px-2.5 py-1 text-[11px] font-medium text-indigo-700">
              {count}
            </span>
          )}
        </div>
      </summary>
      <div className="px-4 pb-4">
        <JsonViewer value={value} />
      </div>
    </details>
  )
}

export function Message({ message, isWelcome = false }: MessageProps) {
  const isUser = message.role === 'user'
  const [entered, setEntered] = useState(false)

  useEffect(() => {
    const id = requestAnimationFrame(() => setEntered(true))
    return () => cancelAnimationFrame(id)
  }, [])

  const timeText = useMemo(() => formatDate(message.timestamp, 'HH:mm'), [message.timestamp])

  const isErrorMessage = useMemo(() => {
    if (isUser) return false
    if (message.data?.error) return true

    const text = message.content.trim()
    return text.startsWith('请求失败') || text.startsWith('Request failed')
  }, [isUser, message.content, message.data?.error])

  if (isWelcome) {
    return (
      <div
        className={`flex justify-center transform-gpu transition-all duration-300 ease-out ${
          entered ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
        }`}
      >
        <div className="w-full max-w-3xl rounded-3xl border border-indigo-100 bg-white/70 p-6 shadow-sm shadow-indigo-100/70 backdrop-blur">
          <div className="flex items-start gap-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-sm shadow-indigo-200/60">
              <span className="text-lg">🌍</span>
            </div>
            <div className="min-w-0">
              <div className="text-lg font-semibold text-gray-900">欢迎来到旅游助手</div>
              <div className="mt-1 whitespace-pre-wrap text-sm leading-relaxed text-gray-600">
                {message.content}
              </div>

              <div className="mt-4 grid gap-2 sm:grid-cols-2">
                {[
                  '我想去成都玩 3 天，预算 2000 元，帮我安排吃住行。',
                  '我计划 2 月从北京去东京，2 人出行，想要性价比高的航班和酒店。',
                  '帮我规划一条适合亲子出游的 5 天游，包含景点 + 美食。',
                  '我已经有目的地和日期了，帮我对比下不同方案并给出推荐。',
                ].map((text) => (
                  <div
                    key={text}
                    className="rounded-2xl border border-gray-200 bg-white/70 px-4 py-3 text-xs leading-relaxed text-gray-600"
                  >
                    {text}
                  </div>
                ))}
              </div>

              <div className="mt-4 flex items-center justify-between gap-3 text-[11px] text-gray-500">
                <span>提示：Enter 发送，Shift + Enter 换行</span>
                <span className="text-gray-400">{timeText}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const bubbleClassName = isUser
    ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm shadow-indigo-200/50'
    : isErrorMessage
      ? 'bg-red-50 text-red-800 border-red-200 shadow-sm'
      : 'bg-white/90 text-gray-900 border-gray-200 shadow-sm'

  const metaTextClassName = isUser ? 'text-indigo-100/90' : 'text-gray-400'

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} transform-gpu transition-all duration-300 ease-out ${
        entered ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}
    >
      <div
        className={`max-w-[92%] md:max-w-[70%] rounded-3xl border px-4 py-3 ${bubbleClassName}`}
      >
        <div className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</div>

        {!isUser && message.data && (
          <div className="mt-4 space-y-3">
            {Array.isArray(message.data.search_results) && message.data.search_results.length > 0 && (
              <DataPanel
                icon="🔎"
                title="搜索结果"
                count={message.data.search_results.length}
                value={message.data.search_results}
              />
            )}

            {Array.isArray(message.data.recommendations) && message.data.recommendations.length > 0 && (
              <DataPanel
                icon="✨"
                title="推荐方案"
                count={message.data.recommendations.length}
                value={message.data.recommendations}
              />
            )}

            {message.data.booking_info && Object.keys(message.data.booking_info).length > 0 && (
              <DataPanel icon="🎫" title="预订信息" value={message.data.booking_info} />
            )}

            {(message.data.status || message.data.error) && (
              <div className="flex flex-wrap items-center justify-between gap-3">
                {message.data.status && (
                  <span className="inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-[11px] font-medium text-indigo-700">
                    <span className="h-1.5 w-1.5 rounded-full bg-indigo-600" />
                    状态：{message.data.status}
                  </span>
                )}
                {message.data.error && (
                  <span className="text-[11px] font-medium text-red-700">{message.data.error}</span>
                )}
              </div>
            )}
          </div>
        )}

        <div className={`mt-2 flex justify-end text-[11px] ${metaTextClassName}`}>{timeText}</div>
      </div>
    </div>
  )
}
