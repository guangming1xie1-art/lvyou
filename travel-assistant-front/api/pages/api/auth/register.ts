import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { createTokenPair } from '@/lib/utils/jwt'
import { findUserByEmail, findUserByUsername } from '@/lib/models/user'
import { createUser } from '@/lib/models/user'
import { validateEmail, validatePassword, validateUsername } from '@/lib/utils/validators'
import type { PublicUser } from '@/lib/models/types'

interface RegisterBody {
  username: string
  email: string
  password: string
  confirmPassword?: string
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
    const { username, email, password, confirmPassword } = req.body as RegisterBody

    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Username, email, and password are required' })
    }

    if (confirmPassword && password !== confirmPassword) {
      return res.status(400).json({ error: 'Passwords do not match' })
    }

    const usernameValidation = validateUsername(username)
    if (!usernameValidation.isValid) {
      return res.status(400).json({ error: usernameValidation.message })
    }

    const emailValidation = validateEmail(email)
    if (!emailValidation.isValid) {
      return res.status(400).json({ error: emailValidation.message })
    }

    const passwordValidation = validatePassword(password)
    if (!passwordValidation.isValid) {
      return res.status(400).json({ error: passwordValidation.message })
    }

    if (findUserByUsername(username)) {
      return res.status(409).json({ error: 'Username already exists' })
    }

    if (findUserByEmail(email)) {
      return res.status(409).json({ error: 'Email already exists' })
    }

    const user = await createUser({ username, email, password })
    const tokens = await createTokenPair(user.id)

    const response: SuccessResponse = {
      access_token: tokens.access_token,
      refresh_token: tokens.refresh_token,
      token_type: 'Bearer',
      expires_in: 3600,
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        is_active: user.is_active,
        created_at: user.created_at,
        last_login: user.last_login,
      },
    }

    return res.status(201).json(response)
  } catch (error) {
    console.error('Registration error:', error)
    return res.status(500).json({ error: 'Internal server error' })
  }
})