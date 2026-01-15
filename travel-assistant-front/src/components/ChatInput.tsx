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
  placeholder = '说点什么…例如：我想去北京旅游 5 天，预算 3000 元',
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

  return (
    <div className="border-t bg-white">
      <div className="container mx-auto px-4 py-4">
        <div className="flex gap-3 items-end">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={placeholder}
            rows={2}
            className="flex-1 resize-none rounded-xl border border-gray-200 px-4 py-3 outline-none focus:ring-2 focus:ring-primary-200 disabled:bg-gray-50"
          />
          <button
            onClick={onSend}
            disabled={disabled || !value.trim()}
            className="px-5 py-3 rounded-xl bg-primary-600 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary-700 transition-colors"
          >
            发送
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-400">Enter 发送，Shift+Enter 换行</div>
      </div>
    </div>
  )
}
