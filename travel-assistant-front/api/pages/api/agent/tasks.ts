import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { db } from '@/lib/models/db'

export default withMiddleware(
  requireAuth(async (req, res) => {
    if (req.method !== 'GET') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
      const limit = parseInt(req.query.limit as string) || 50
      const tasks = db.tasks.slice(0, limit)

      return res.status(200).json({
        total: db.tasks.length,
        filtered: tasks.length,
        tasks,
      })
    } catch (error) {
      console.error('Get tasks error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)