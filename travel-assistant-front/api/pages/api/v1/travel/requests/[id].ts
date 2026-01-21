import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { getTravelRequest, updateTravelRequest, deleteTravelRequest } from '@/lib/models/travel'
import type { DbTravelRequest } from '@/lib/models/types'

export default withMiddleware(
  requireAuth(async (req, res) => {
    const requestId = req.query.id as string

    if (!requestId) {
      return res.status(400).json({ error: 'Request ID is required' })
    }

    try {
      if (req.method === 'GET') {
        const request = getTravelRequest(requestId, req.userId!)
        
        if (!request) {
          return res.status(404).json({ error: 'Travel request not found' })
        }

        return res.status(200).json({ request })
      }

      if (req.method === 'PUT') {
        const {
          destination,
          departure_date,
          return_date,
          people_count,
          budget,
          is_domestic,
          preferences,
          special_requirements,
        } = req.body

        const updated = updateTravelRequest(requestId, req.userId!, {
          destination,
          departure_date,
          return_date,
          people_count,
          budget,
          is_domestic,
          preferences,
          special_requirements,
        })

        if (!updated) {
          return res.status(404).json({ error: 'Travel request not found' })
        }

        return res.status(200).json({ request: updated })
      }

      if (req.method === 'DELETE') {
        const deleted = deleteTravelRequest(requestId, req.userId!)

        if (!deleted) {
          return res.status(404).json({ error: 'Travel request not found' })
        }

        return res.status(204).end()
      }

      return res.status(405).json({ error: 'Method not allowed' })
    } catch (error) {
      console.error('Travel request detail error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)