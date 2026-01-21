import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { getRestaurant } from '@/lib/routes/attractions'
import type { DbRestaurant } from '@/lib/models/types'

export default withMiddleware(async (req, res) => {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const restaurantId = req.query.id as string

    if (!restaurantId) {
      return res.status(400).json({ error: 'Restaurant ID is required' })
    }

    const restaurant = getRestaurant(restaurantId)

    if (!restaurant) {
      return res.status(404).json({ error: 'Restaurant not found' })
    }

    return res.status(200).json({ restaurant })
  } catch (error) {
    console.error('Get restaurant error:', error)
    return res.status(500).json({ error: 'Internal server error' })
  }
})