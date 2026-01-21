import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { getOrder, updateOrder } from '@/lib/models/order'
import type { DbOrder } from '@/lib/models/types'

interface UpdateOrderBody {
  contact_name?: string
  contact_phone?: string
  contact_email?: string
  notes?: string
}

export default withMiddleware(
  requireAuth(async (req, res) => {
    const orderId = req.query.id as string

    if (!orderId) {
      return res.status(400).json({ error: 'Order ID is required' })
    }

    try {
      if (req.method === 'GET') {
        const order = getOrder(orderId, req.userId!)

        if (!order) {
          return res.status(404).json({ error: 'Order not found' })
        }

        return res.status(200).json({ order })
      }

      if (req.method === 'PUT') {
        const updateData = req.body as UpdateOrderBody

        const updated = updateOrder(orderId, req.userId!, updateData)

        if (!updated) {
          return res.status(404).json({ error: 'Order not found' })
        }

        return res.status(200).json({ order: updated })
      }

      return res.status(405).json({ error: 'Method not allowed' })
    } catch (error) {
      console.error('Order detail error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)