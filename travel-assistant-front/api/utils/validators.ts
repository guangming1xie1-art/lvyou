import { clamp } from './generators'

export function asString(v: unknown): string | null {
  return typeof v === 'string' && v.trim() ? v : null
}

export function asNumber(v: unknown): number | null {
  if (typeof v === 'number' && Number.isFinite(v)) return v
  if (typeof v === 'string' && v.trim() && Number.isFinite(Number(v))) return Number(v)
  return null
}

export function parsePagination(query: Record<string, unknown>): { page: number; page_size: number } {
  const page = clamp(asNumber(query.page) ?? 1, 1, 10000)
  const page_size = clamp(asNumber(query.page_size) ?? 10, 1, 100)
  return { page, page_size }
}

export function requireBody<T extends object>(body: unknown): T {
  if (!body || typeof body !== 'object') {
    throw new Error('Invalid JSON body')
  }
  return body as T
}
