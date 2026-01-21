import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { getPlan } from '@/lib/models/travel'
import type { DbTravelPlan } from '@/lib/models/types'

interface CompareRequest {
  plan_ids: string[]
}

interface CompareResponse {
  plans: DbTravelPlan[]
  comparison: {
    total_cost_min: number
    total_cost_max: number
    total_cost_avg: number
    days_min: number
    days_max: number
    highlights: string[]
  }
}

export default withMiddleware(
  requireAuth(async (req, res) => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
      const { plan_ids } = req.body as CompareRequest

      if (!plan_ids || !Array.isArray(plan_ids) || plan_ids.length === 0) {
        return res.status(400).json({ error: 'plan_ids array is required' })
      }

      if (plan_ids.length > 5) {
        return res.status(400).json({ error: 'Maximum 5 plans can be compared' })
      }

      const plans = plan_ids
        .map(id => getPlan(id, req.userId!))
        .filter((plan): plan is DbTravelPlan => plan !== null)

      if (plans.length === 0) {
        return res.status(404).json({ error: 'No valid plans found' })
      }

      const totalCosts = plans.map(p => p.total_cost)
      const daysCounts = plans.map(p => p.daily_itinerary.length)

      const allHighlights = plans.flatMap(p => p.highlights)
      const uniqueHighlights = [...new Set(allHighlights)].slice(0, 10)

      const response: CompareResponse = {
        plans,
        comparison: {
          total_cost_min: Math.min(...totalCosts),
          total_cost_max: Math.max(...totalCosts),
          total_cost_avg: totalCosts.reduce((a, b) => a + b, 0) / totalCosts.length,
          days_min: Math.min(...daysCounts),
          days_max: Math.max(...daysCounts),
          highlights: uniqueHighlights,
        },
      }

      return res.status(200).json(response)
    } catch (error) {
      console.error('Plan comparison error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)