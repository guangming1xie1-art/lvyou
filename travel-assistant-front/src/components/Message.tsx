import type { ChatMessage } from '@/types/chat'

interface MessageProps {
  message: ChatMessage
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[92%] md:max-w-[70%] rounded-2xl px-4 py-3 shadow-sm border ${
          isUser
            ? 'bg-primary-600 text-white border-primary-600'
            : 'bg-white text-gray-900 border-gray-100'
        }`}
      >
        <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>

        {!isUser && message.data && (
          <div className="mt-3 space-y-3">
            {message.data.search_results?.length > 0 && (
              <details className="rounded-xl border border-gray-100 bg-gray-50 p-3">
                <summary className="cursor-pointer font-medium">搜索结果（{message.data.search_results.length}）</summary>
                <pre className="mt-2 overflow-auto text-xs text-gray-700">
                  {JSON.stringify(message.data.search_results, null, 2)}
                </pre>
              </details>
            )}

            {message.data.recommendations?.length > 0 && (
              <details className="rounded-xl border border-gray-100 bg-gray-50 p-3">
                <summary className="cursor-pointer font-medium">推荐方案（{message.data.recommendations.length}）</summary>
                <pre className="mt-2 overflow-auto text-xs text-gray-700">
                  {JSON.stringify(message.data.recommendations, null, 2)}
                </pre>
              </details>
            )}

            {message.data.booking_info && Object.keys(message.data.booking_info).length > 0 && (
              <details className="rounded-xl border border-gray-100 bg-gray-50 p-3">
                <summary className="cursor-pointer font-medium">预订信息</summary>
                <pre className="mt-2 overflow-auto text-xs text-gray-700">
                  {JSON.stringify(message.data.booking_info, null, 2)}
                </pre>
              </details>
            )}

            {message.data.status && (
              <div className="text-xs text-gray-500">状态：{message.data.status}</div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
