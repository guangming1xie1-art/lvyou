import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from './withMiddleware'
import { verifyToken } from '@/lib/utils/jwt'
import type { PublicUser } from '@/lib/models/types'
import { findUserById } from '@/lib/models/user'

export interface AuthenticatedRequest extends NextApiRequest {
  userId?: string
  user?: PublicUser
}

export function requireAuth(handler: (req: AuthenticatedRequest, res: NextApiResponse) => Promise<void> | void) {
  return withMiddleware(async (req: AuthenticatedRequest, res: NextApiResponse) => {
    const authHeader = req.headers.authorization

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Authorization header required' })
    }

    const token = authHeader.substring(7) // Remove 'Bearer ' prefix

    try {
      const claims = verifyToken(token)
      
      if (!claims.sub) {
        return res.status(401).json({ error: 'Invalid token' })
      }

      const user = findUserById(claims.sub)
      
      if (!user || !user.is_active) {
        return res.status(401).json({ error: 'User not found or inactive' })
      }

      req.userId = claims.sub
      req.user = {
        id: user.id,
        username: user.username,
        email: user.email,
        is_active: user.is_active,
        created_at: user.created_at,
        last_login: user.last_login,
      }

      await handler(req, res)
    } catch (error) {
      console.error('Auth verification error:', error)
      return res.status(401).json({ error: 'Invalid or expired token' })
    }
  })
}