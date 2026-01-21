import type { NextApiRequest, NextApiResponse } from 'next'
import { requireAuth } from '../middlewares/auth'
import { createOrder, getOrder, listOrders, payOrder, cancelOrder, updateOrder } from '../models/order'
import { sendError, sendWrapped } from '../utils/response'
import { asString, parsePagination, requireBody } from '../utils/validators'

export async function handleOrdersRoute(req: NextApiRequest, res: NextApiResponse, segments: string[]): Promise<void> {
  const user = requireAuth(req, res)
  if (!user) return

  const orderId = segments[1]

  if (!orderId) {
    if (req.method === 'POST') {
      try {
        const body = requireBody<Record<string, unknown>>(req.body)
        const plan_id = asString(body.plan_id)
        const contact_name = asString(body.contact_name)
        const contact_phone = asString(body.contact_phone)
        const contact_email = asString(body.contact_email)
        const notes = asString(body.notes) || undefined

        if (!plan_id || !contact_name || !contact_phone || !contact_email) {
          sendError(res, 400, 'plan_id, contact_name, contact_phone, contact_email are required')
          return
        }

        const order = createOrder({
          user_id: user.id,
          plan_id,
          contact_name,
          contact_phone,
          contact_email,
          notes,
        })
        sendWrapped(res, order)
      } catch (e) {
        sendError(res, 400, e instanceof Error ? e.message : 'Bad request')
      }
      return
    }

    if (req.method === 'GET') {
      const { page, page_size } = parsePagination(req.query as any)
      const status = asString(req.query.status)
      const all = listOrders(user.id)
        .filter((o) => (status ? o.status === status : true))
        .sort((a, b) => (a.created_at < b.created_at ? 1 : -1))

      const start = (page - 1) * page_size
      const items = all.slice(start, start + page_size)

      sendWrapped(res, {
        items,
        total: all.length,
        page,
        page_size,
        total_pages: Math.ceil(all.length / page_size) || 1,
      })
      return
    }

    sendError(res, 405, 'Method not allowed')
    return
  }

  if (segments[2] === 'cancel' && req.method === 'POST') {
    const order = cancelOrder(user.id, orderId)
    if (!order) {
      sendError(res, 404, 'Order not found')
      return
    }
    sendWrapped(res, order)
    return
  }

  if (segments[2] === 'pay' && req.method === 'POST') {
    const result = payOrder(user.id, orderId)
    if (!result) {
      sendError(res, 404, 'Order not found')
      return
    }
    sendWrapped(res, { payment_url: result.payment_url })
    return
  }

  if (req.method === 'GET') {
    const order = getOrder(user.id, orderId)
    if (!order) {
      sendError(res, 404, 'Order not found')
      return
    }
    sendWrapped(res, order)
    return
  }

  if (req.method === 'PUT') {
    try {
      const patch = requireBody<Record<string, unknown>>(req.body)
      const updated = updateOrder(user.id, orderId, patch as any)
      if (!updated) {
        sendError(res, 404, 'Order not found')
        return
      }
      sendWrapped(res, updated)
    } catch (e) {
      sendError(res, 400, e instanceof Error ? e.message : 'Bad request')
    }
    return
  }

  sendError(res, 405, 'Method not allowed')
}
