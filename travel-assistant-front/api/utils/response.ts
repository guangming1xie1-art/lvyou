import type { NextApiResponse } from 'next'

export interface ApiWrapper<T> {
  code: number
  message: string
  data: T
}

export function sendWrapped<T>(res: NextApiResponse, data: T, message = 'success', code = 200): void {
  const payload: ApiWrapper<T> = { code, message, data }
  res.status(200).json(payload)
}

export function sendError(res: NextApiResponse, status: number, message: string, code?: number): void {
  res.status(status).json({ code: code ?? status, message, data: null })
}
