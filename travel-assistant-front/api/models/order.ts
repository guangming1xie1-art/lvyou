import { db } from './db'
import type { DbOrder } from './types'
import { nowIso, uuid } from '../utils/generators'
import { getPlan } from './travel'

export function createOrder(params: {
  user_id: string
  plan_id: string
  contact_name: string
  contact_phone: string
  contact_email: string
  notes?: string
}): DbOrder {
  const plan = getPlan(params.plan_id)
  const total_amount = plan?.total_cost ?? 0
  const ts = nowIso()

  const order: DbOrder = {
    order_id: uuid(),
    user_id: params.user_id,
    plan_id: params.plan_id,
    status: 'pending',
    total_amount,
    payment_status: 'unpaid',
    contact_name: params.contact_name,
    contact_phone: params.contact_phone,
    contact_email: params.contact_email,
    notes: params.notes,
    created_at: ts,
    updated_at: ts,
  }

  db.orders.push(order)
  return order
}

export function listOrders(userId: string): DbOrder[] {
  return db.orders.filter((o) => o.user_id === userId)
}

export function getOrder(userId: string, orderId: string): DbOrder | undefined {
  return db.orders.find((o) => o.user_id === userId && o.order_id === orderId)
}

export function updateOrder(userId: string, orderId: string, patch: Partial<DbOrder>): DbOrder | undefined {
  const order = getOrder(userId, orderId)
  if (!order) return undefined

  const immutable = new Set(['order_id', 'user_id', 'plan_id', 'created_at'])
  for (const [k, v] of Object.entries(patch)) {
    if (immutable.has(k)) continue
    ;(order as any)[k] = v
  }

  order.updated_at = nowIso()
  return order
}

export function cancelOrder(userId: string, orderId: string): DbOrder | undefined {
  const order = getOrder(userId, orderId)
  if (!order) return undefined
  if (order.status === 'cancelled') return order

  order.status = 'cancelled'
  order.payment_status = order.payment_status === 'paid' ? 'refunded' : order.payment_status
  order.updated_at = nowIso()
  return order
}

export function payOrder(userId: string, orderId: string): { order: DbOrder; payment_url: string } | undefined {
  const order = getOrder(userId, orderId)
  if (!order) return undefined

  if (order.status === 'cancelled') return { order, payment_url: '' }

  order.payment_status = 'paid'
  order.status = order.status === 'pending' ? 'confirmed' : order.status
  order.updated_at = nowIso()

  return {
    order,
    payment_url: `https://pay.mock.local/checkout?order_id=${order.order_id}`,
  }
}
