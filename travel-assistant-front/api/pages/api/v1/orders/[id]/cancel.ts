import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { cancelOrder } from '@/lib/models/order'
import type { DbOrder } from '@/lib/models/types'

export default withMiddleware(
  requireAuth(async (req, res) => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    const orderId = req.query.id as string
    if (!orderId) {
      return res.status(400).json({ error: 'Order ID is required' })
    }

    try {
      const order = cancelOrder(orderId, req.userId!)

      if (!order) {
        return res.status(404).json({ error: 'Order not found' })
      }

      return res.status(200).json({ order })
    } catch (error) {
      console.error('Cancel order error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)