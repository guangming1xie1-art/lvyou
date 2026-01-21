import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { verifyToken, issueAccessToken } from '@/lib/utils/jwt'
import { findUserById } from '@/lib/models/user'
import type { PublicUser } from '@/lib/models/types'

interface RefreshBody {
  refresh_token: string
  user_id?: string
}

interface SuccessResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: PublicUser
}

export default withMiddleware(async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { refresh_token } = req.body as RefreshBody

    if (!refresh_token) {
      return res.status(400).json({ error: 'Refresh token is required' })
    }

    let claims: any
    try {
      claims = verifyToken(refresh_token)
    } catch {
      return res.status(401).json({ error: 'Invalid or expired refresh token' })
    }

    if (claims.typ !== 'refresh') {
      return res.status(401).json({ error: 'Invalid token type' })
    }

    const user = findUserById(claims.sub)
    if (!user || !user.is_active) {
      return res.status(401).json({ error: 'User not found or inactive' })
    }

    const accessToken = issueAccessToken({
      id: user.id,
      username: user.username,
      email: user.email,
      is_active: user.is_active,
      created_at: user.created_at,
      last_login: user.last_login,
    })

    const response: SuccessResponse = {
      access_token: accessToken.token,
      token_type: 'Bearer',
      expires_in: accessToken.expires_in,
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        is_active: user.is_active,
        created_at: user.created_at,
        last_login: user.last_login,
      },
    }

    return res.status(200).json(response)
  } catch (error) {
    console.error('Token refresh error:', error)
    return res.status(500).json({ error: 'Internal server error' })
  }
})