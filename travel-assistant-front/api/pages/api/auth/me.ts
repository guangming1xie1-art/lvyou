import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { findUserById } from '@/lib/models/user'
import type { PublicUser } from '@/lib/models/types'

interface SuccessResponse {
  user: PublicUser
}

export default withMiddleware(
  requireAuth(async (req, res) => {
    try {
      const userId = req.userId

      if (!userId) {
        return res.status(401).json({ error: 'Unauthorized' })
      }

      const user = findUserById(userId)
      if (!user) {
        return res.status(404).json({ error: 'User not found' })
      }

      if (!user.is_active) {
        return res.status(403).json({ error: 'Account is deactivated' })
      }

      const response: SuccessResponse = {
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
      console.error('Get current user error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)