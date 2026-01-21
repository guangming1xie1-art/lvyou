import type { NextApiRequest, NextApiResponse } from 'next'

export function applyCors(req: NextApiRequest, res: NextApiResponse): void {
  const origin = req.headers.origin
  res.setHeader('Access-Control-Allow-Origin', origin || '*')
  res.setHeader('Vary', 'Origin')
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')
  res.setHeader('Access-Control-Max-Age', '86400')
}

export function handlePreflight(req: NextApiRequest, res: NextApiResponse): boolean {
  if (req.method === 'OPTIONS') {
    applyCors(req, res)
    res.status(200).end()
    return true
  }
  return false
}
