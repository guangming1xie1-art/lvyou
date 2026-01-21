import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { payOrder } from '@/lib/models/order'

interface PayResponse {
  payment_url: string
  message: string
}

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
      const result = payOrder(orderId, req.userId!)

      if (!result) {
        return res.status(404).json({ error: 'Order not found' })
      }

      const response: PayResponse = {
        payment_url: result.payment_url,
        message: 'Payment initiated successfully',
      }

      return res.status(200).json(response)
    } catch (error) {
      console.error('Pay order error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)