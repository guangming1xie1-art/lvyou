import type { NextApiRequest, NextApiResponse } from 'next'
import { applyCors, handlePreflight } from './cors'

export type Handler = (req: NextApiRequest, res: NextApiResponse) => Promise<void> | void

export function withMiddleware(handler: Handler): Handler {
  return async (req: NextApiRequest, res: NextApiResponse): Promise<void> => {
    try {
      applyCors(req, res)

      if (handlePreflight(req, res)) {
        return
      }

      await handler(req, res)
    } catch (error) {
      console.error('Middleware error:', error)
      if (!res.headersSent) {
        res.status(500).json({ error: 'Internal server error' })
      }
    }
  }
}

export interface AuthenticatedRequest extends NextApiRequest {
  userId?: string
}