import { useEffect, useRef, type KeyboardEvent } from 'react'

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({
  value,
  onChange,
  onSend,
  disabled = false,
  placeholder = '描述一下你的行程：目的地 / 天数 / 人数 / 预算 / 偏好…',
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)

  useEffect(() => {
    textareaRef.current?.focus()
  }, [])

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (!disabled) onSend()
    }
  }

  const canSend = !disabled && Boolean(value.trim())

  return (
    <div className="sticky bottom-0 border-t border-indigo-100 bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container mx-auto px-4 py-4">
        <div className="rounded-2xl border border-indigo-100 bg-white/70 p-3 shadow-sm shadow-indigo-100/70 transition-transform duration-200 focus-within:scale-[1.01]">
          <div className="flex gap-3 items-end">
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={disabled}
              placeholder={placeholder}
              rows={2}
              className="flex-1 resize-none rounded-xl border border-indigo-200 bg-white px-4 py-3 text-sm leading-relaxed text-gray-900 placeholder:text-gray-400 outline-none transition-all duration-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 disabled:bg-gray-50 disabled:text-gray-400"
            />
            <button
              onClick={onSend}
              disabled={!canSend}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-sm shadow-indigo-200/60 transition-all duration-200 hover:bg-indigo-700 hover:shadow-indigo-200/80 hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:bg-indigo-300 disabled:text-white/80 disabled:shadow-none"
            >
              发送
              <svg
                viewBox="0 0 24 24"
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M22 2L11 13" />
                <path d="M22 2L15 22l-4-9-9-4 20-7z" />
              </svg>
            </button>
          </div>

          <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-[11px] text-gray-500">
            <span>Enter 发送 · Shift+Enter 换行</span>
            <span className="hidden sm:inline">建议包含：出发地、目的地、日期、预算、偏好</span>
          </div>
        </div>
      </div>
    </div>
  )
}
