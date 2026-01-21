import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { getAttraction } from '@/lib/routes/attractions'
import type { DbAttraction } from '@/lib/models/types'

export default withMiddleware(async (req, res) => {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const attractionId = req.query.id as string

    if (!attractionId) {
      return res.status(400).json({ error: 'Attraction ID is required' })
    }

    const attraction = getAttraction(attractionId)

    if (!attraction) {
      return res.status(404).json({ error: 'Attraction not found' })
    }

    return res.status(200).json({ attraction })
  } catch (error) {
    console.error('Get attraction error:', error)
    return res.status(500).json({ error: 'Internal server error' })
  }
})