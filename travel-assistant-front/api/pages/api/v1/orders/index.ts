import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { createOrder, listOrders } from '@/lib/models/order'
import type { DbOrder } from '@/lib/models/types'

interface CreateOrderBody {
  plan_id: string
  contact_name: string
  contact_phone: string
  contact_email: string
  notes?: string
}

export default withMiddleware(
  requireAuth(async (req, res) => {
    try {
      if (req.method === 'GET') {
        const page = parseInt(req.query.page as string) || 1
        const pageSize = parseInt(req.query.page_size as string) || 10
        const status = req.query.status as string

        const result = listOrders(req.userId!, page, pageSize, status)
        return res.status(200).json(result)
      }

      if (req.method === 'POST') {
        const {
          plan_id,
          contact_name,
          contact_phone,
          contact_email,
          notes,
        } = req.body as CreateOrderBody

        if (!plan_id || !contact_name || !contact_phone || !contact_email) {
          return res.status(400).json({ error: 'plan_id, contact_name, contact_phone, contact_email are required' })
        }

        const order = createOrder({
          user_id: req.userId!,
          plan_id,
          contact_name,
          contact_phone,
          contact_email,
          notes,
        })

        return res.status(201).json({ order })
      }

      return res.status(405).json({ error: 'Method not allowed' })
    } catch (error) {
      console.error('Order error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)