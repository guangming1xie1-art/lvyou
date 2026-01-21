import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { listPlansByRequestId } from '@/lib/models/travel'

export default withMiddleware(
  requireAuth(async (req, res) => {
    if (req.method !== 'GET') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
      const requestId = req.query.request_id as string
      const page = parseInt(req.query.page as string) || 1
      const pageSize = parseInt(req.query.page_size as string) || 10

      if (!requestId) {
        return res.status(400).json({ error: 'request_id parameter is required' })
      }

      const result = listPlansByRequestId(requestId, req.userId!, page, pageSize)
      
      return res.status(200).json(result)
    } catch (error) {
      console.error('List plans error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)