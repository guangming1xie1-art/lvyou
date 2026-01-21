import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { createTokenPair } from '@/lib/utils/jwt'
import { verifyPassword } from '@/lib/utils/password'
import { findUserByUsername, touchLastLogin, toPublicUser } from '@/lib/models/user'
import type { PublicUser } from '@/lib/models/types'

interface LoginBody {
  username: string
  password: string
}

interface SuccessResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: PublicUser
}

export default withMiddleware(async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { username, password } = req.body as LoginBody

    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' })
    }

    const user = findUserByUsername(username)
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' })
    }

    const isValid = await verifyPassword(password, user.password_hash)
    if (!isValid) {
      return res.status(401).json({ error: 'Invalid credentials' })
    }

    if (!user.is_active) {
      return res.status(403).json({ error: 'Account is deactivated' })
    }

    touchLastLogin(user.id)

    const tokens = await createTokenPair(user.id)

    const response: SuccessResponse = {
      access_token: tokens.access_token,
      refresh_token: tokens.refresh_token,
      token_type: 'Bearer',
      expires_in: 3600,
      user: toPublicUser(user),
    }

    return res.status(200).json(response)
  } catch (error) {
    console.error('Login error:', error)
    return res.status(500).json({ error: 'Internal server error' })
  }
})