import type { NextApiRequest, NextApiResponse } from 'next'
import type { AccessTokenClaims } from '../utils/jwt'
import { verifyToken } from '../utils/jwt'
import { findUserById, toPublicUser } from '../models/user'

export function getBearerToken(req: NextApiRequest): string | null {
  const auth = req.headers.authorization
  if (!auth) return null
  const m = /^Bearer\s+(.+)$/.exec(auth)
  return m?.[1] ?? null
}

export function requireAuth(req: NextApiRequest, res: NextApiResponse) {
  const token = getBearerToken(req)
  if (!token) {
    res.status(401).json({ code: 401, message: 'Missing Authorization header', detail: 'Missing Authorization header' })
    return null
  }

  try {
    const claims = verifyToken<AccessTokenClaims>(token)
    if (claims.typ !== 'access') {
      res.status(401).json({ code: 401, message: 'Invalid token type', detail: 'Invalid token type' })
      return null
    }

    const user = findUserById(claims.sub)
    if (!user) {
      res.status(401).json({ code: 401, message: 'User not found', detail: 'User not found' })
      return null
    }

    if (!user.is_active) {
      res.status(403).json({ code: 403, message: 'User is inactive', detail: 'User is inactive' })
      return null
    }

    return toPublicUser(user)
  } catch {
    res.status(401).json({ code: 401, message: 'Invalid or expired token', detail: 'Invalid or expired token' })
    return null
  }
}
