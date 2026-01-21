import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { db } from '@/lib/models/db'
import type { DbAgentTask } from '@/lib/models/types'

export default withMiddleware(
  requireAuth(async (req, res) => {
    if (req.method !== 'GET') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    const taskId = req.query.taskId as string
    if (!taskId) {
      return res.status(400).json({ error: 'Task ID is required' })
    }

    try {
      const task = db.tasks.find(t => t.task_id === taskId)

      if (!task) {
        return res.status(404).json({ error: 'Task not found' })
      }

      return res.status(200).json(task)
    } catch (error) {
      console.error('Get task status error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)