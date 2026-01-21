import type { NextApiRequest, NextApiResponse } from 'next'
import { db } from '../models/db'
import { createUser, findUserByEmail, findUserByUsername, toPublicUser, touchLastLogin } from '../models/user'
import { verifyPassword } from '../utils/password'
import type { RefreshTokenClaims } from '../utils/jwt'
import { issueAccessToken, issueRefreshToken, verifyToken } from '../utils/jwt'
import { nowIso } from '../utils/generators'
import { requireAuth } from '../middlewares/auth'

function revokeAllRefreshTokens(userId: string): void {
  for (const rt of db.refresh_tokens) {
    if (rt.user_id === userId) rt.revoked = true
  }
}

export async function handleAuthRoute(req: NextApiRequest, res: NextApiResponse, segments: string[]): Promise<void> {
  const action = segments[0] || ''

  if (action === 'register' && req.method === 'POST') {
    const { username, email, password, confirm_password } = (req.body || {}) as Record<string, unknown>
    if (!username || !email || !password) {
      res.status(400).json({ detail: 'username, email and password are required' })
      return
    }
    if (confirm_password && confirm_password !== password) {
      res.status(400).json({ detail: 'Passwords do not match' })
      return
    }

    if (findUserByUsername(String(username))) {
      res.status(409).json({ detail: 'Username already exists' })
      return
    }
    if (findUserByEmail(String(email))) {
      res.status(409).json({ detail: 'Email already exists' })
      return
    }

    const user = await createUser({ username: String(username), email: String(email), password: String(password) })
    res.status(201).json(toPublicUser(user))
    return
  }

  if (action === 'login' && req.method === 'POST') {
    const { username, password } = (req.body || {}) as Record<string, unknown>
    if (!username || !password) {
      res.status(400).json({ detail: 'username and password are required' })
      return
    }

    const user = findUserByUsername(String(username))
    if (!user) {
      res.status(401).json({ detail: 'Invalid credentials' })
      return
    }

    const ok = await verifyPassword(String(password), user.password_hash)
    if (!ok) {
      res.status(401).json({ detail: 'Invalid credentials' })
      return
    }

    touchLastLogin(user.id)

    const publicUser = toPublicUser(user)
    const access = issueAccessToken(publicUser)
    const refresh = issueRefreshToken(publicUser)

    db.refresh_tokens.push({
      token: refresh.token,
      user_id: publicUser.id,
      created_at: nowIso(),
      expires_at: refresh.expires_at,
      revoked: false,
    })

    res.status(200).json({
      user: { ...publicUser, last_login: publicUser.last_login ?? undefined },
      tokens: {
        access_token: access.token,
        refresh_token: refresh.token,
        token_type: 'Bearer',
        expires_in: access.expires_in,
      },
    })
    return
  }

  if (action === 'refresh' && req.method === 'POST') {
    const { refresh_token } = (req.body || {}) as Record<string, unknown>
    if (!refresh_token || typeof refresh_token !== 'string') {
      res.status(400).json({ detail: 'refresh_token is required' })
      return
    }

    let claims: RefreshTokenClaims
    try {
      claims = verifyToken<RefreshTokenClaims>(refresh_token)
    } catch {
      res.status(401).json({ detail: 'Invalid refresh token' })
      return
    }

    if (claims.typ !== 'refresh') {
      res.status(401).json({ detail: 'Invalid token type' })
      return
    }

    const record = db.refresh_tokens.find((t) => t.token === refresh_token)
    if (!record || record.revoked) {
      res.status(401).json({ detail: 'Refresh token revoked' })
      return
    }

    const user = db.users.find((u) => u.id === claims.sub)
    if (!user) {
      res.status(401).json({ detail: 'User not found' })
      return
    }

    const publicUser = toPublicUser(user)
    const access = issueAccessToken(publicUser)
    const refresh = issueRefreshToken(publicUser)

    record.revoked = true
    record.replaced_by = refresh.token

    db.refresh_tokens.push({
      token: refresh.token,
      user_id: publicUser.id,
      created_at: nowIso(),
      expires_at: refresh.expires_at,
      revoked: false,
    })

    res.status(200).json({
      access_token: access.token,
      refresh_token: refresh.token,
      token_type: 'Bearer',
      expires_in: access.expires_in,
    })
    return
  }

  if (action === 'me' && req.method === 'GET') {
    const user = requireAuth(req, res)
    if (!user) return
    res.status(200).json({ ...user, last_login: user.last_login ?? undefined })
    return
  }

  if (action === 'logout' && req.method === 'POST') {
    const user = requireAuth(req, res)
    if (!user) return
    revokeAllRefreshTokens(user.id)
    res.status(200).json({ ok: true })
    return
  }

  res.status(404).json({ detail: 'Not found' })
}
