import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { getPlan } from '@/lib/models/travel'
import type { DbTravelPlan } from '@/lib/models/types'

export default withMiddleware(
  requireAuth(async (req, res) => {
    if (req.method !== 'GET') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
      const planId = req.query.id as string

      if (!planId) {
        return res.status(400).json({ error: 'Plan ID is required' })
      }

      const plan = getPlan(planId, req.userId!)

      if (!plan) {
        return res.status(404).json({ error: 'Travel plan not found' })
      }

      return res.status(200).json({ plan })
    } catch (error) {
      console.error('Get travel plan error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)