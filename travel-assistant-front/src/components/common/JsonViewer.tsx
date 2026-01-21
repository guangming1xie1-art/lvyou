import { Fragment } from 'react'

type JsonViewerProps = {
  value: unknown
  className?: string
  defaultExpanded?: boolean
}

const isPlainObject = (value: unknown): value is Record<string, unknown> => {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

const formatScalar = (value: unknown) => {
  if (value === null) return { text: 'null', className: 'text-fuchsia-700' }

  switch (typeof value) {
    case 'string':
      return { text: `"${value}"`, className: 'text-emerald-700' }
    case 'number':
      return { text: String(value), className: 'text-amber-700' }
    case 'boolean':
      return { text: value ? 'true' : 'false', className: 'text-sky-700' }
    case 'undefined':
      return { text: 'undefined', className: 'text-gray-500' }
    default:
      return { text: String(value), className: 'text-gray-700' }
  }
}

function JsonNode({
  name,
  value,
  depth,
  defaultExpanded,
}: {
  name?: string
  value: unknown
  depth: number
  defaultExpanded: boolean
}) {
  const indentClass = depth > 0 ? 'pl-4 border-l border-indigo-100' : ''

  if (Array.isArray(value)) {
    const summary = name ? `"${name}": [` : '['

    return (
      <div className={indentClass}>
        <details open={defaultExpanded} className="group">
          <summary className="cursor-pointer select-none list-none inline-flex items-center gap-2 text-gray-800">
            <span className="font-medium text-indigo-700">{summary}</span>
            <span className="text-gray-500">{value.length}</span>
            <span className="font-medium text-indigo-700">]</span>
            <span className="ml-1 text-[11px] text-gray-400 group-open:hidden">点击展开</span>
          </summary>

          <div className="mt-2 space-y-2">
            {value.length === 0 ? (
              <div className="text-gray-500">(空数组)</div>
            ) : (
              value.map((item, idx) => (
                <JsonNode
                  key={idx}
                  name={String(idx)}
                  value={item}
                  depth={depth + 1}
                  defaultExpanded={false}
                />
              ))
            )}
          </div>
        </details>
      </div>
    )
  }

  if (isPlainObject(value)) {
    const keys = Object.keys(value)
    const summary = name ? `"${name}": {` : '{'

    return (
      <div className={indentClass}>
        <details open={defaultExpanded} className="group">
          <summary className="cursor-pointer select-none list-none inline-flex items-center gap-2 text-gray-800">
            <span className="font-medium text-indigo-700">{summary}</span>
            <span className="text-gray-500">{keys.length}</span>
            <span className="font-medium text-indigo-700">}</span>
            <span className="ml-1 text-[11px] text-gray-400 group-open:hidden">点击展开</span>
          </summary>

          <div className="mt-2 space-y-2">
            {keys.length === 0 ? (
              <div className="text-gray-500">(空对象)</div>
            ) : (
              keys.map((key) => (
                <JsonNode
                  key={key}
                  name={key}
                  value={value[key]}
                  depth={depth + 1}
                  defaultExpanded={false}
                />
              ))
            )}
          </div>
        </details>
      </div>
    )
  }

  const scalar = formatScalar(value)

  return (
    <div className={indentClass}>
      <div className="flex flex-wrap items-start gap-x-2 gap-y-1">
        {name !== undefined && (
          <Fragment>
            <span className="font-medium text-indigo-700">"{name}"</span>
            <span className="text-gray-400">:</span>
          </Fragment>
        )}
        <span className={scalar.className}>{scalar.text}</span>
      </div>
    </div>
  )
}

export function JsonViewer({ value, className = '', defaultExpanded = true }: JsonViewerProps) {
  return (
    <div
      className={`rounded-xl border border-indigo-100 bg-white/80 p-3 text-xs font-mono leading-relaxed text-gray-800 shadow-sm shadow-indigo-100/60 ${className}`}
    >
      <div className="max-h-72 overflow-auto">
        <JsonNode value={value} depth={0} defaultExpanded={defaultExpanded} />
      </div>
    </div>
  )
}
