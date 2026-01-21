import type { NextApiRequest, NextApiResponse } from 'next'
import { requireAuth } from '../middlewares/auth'
import { sendError, sendWrapped } from '../utils/response'
import { asString, parsePagination, requireBody } from '../utils/validators'
import {
  comparePlans,
  createTravelRequest,
  deleteTravelRequest,
  getPlan,
  getPlansForRequest,
  getTravelRequest,
  listTravelRequests,
  updateTravelRequest,
} from '../models/travel'
import type { TravelRequestInput } from '../models/types'

export async function handleTravelRoute(req: NextApiRequest, res: NextApiResponse, segments: string[]): Promise<void> {
  const user = requireAuth(req, res)
  if (!user) return

  // /travel/requests...
  if (segments[0] === 'requests') {
    const requestId = segments[1]

    if (!requestId) {
      if (req.method === 'POST') {
        try {
          const body = requireBody<TravelRequestInput>(req.body)
          const created = createTravelRequest(user.id, body)
          sendWrapped(res, created)
        } catch (e) {
          sendError(res, 400, e instanceof Error ? e.message : 'Bad request')
        }
        return
      }

      if (req.method === 'GET') {
        const { page, page_size } = parsePagination(req.query as any)
        const destination = asString(req.query.destination)
        const keyword = asString(req.query.keyword)?.toLowerCase()

        const all = listTravelRequests(user.id)
          .filter((r) => {
            if (destination && r.destination !== destination) return false
            if (!keyword) return true
            return (
              r.destination.toLowerCase().includes(keyword) ||
              (r.preferences || []).some((p) => p.toLowerCase().includes(keyword)) ||
              (r.special_requirements || '').toLowerCase().includes(keyword)
            )
          })
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

    // /travel/requests/:id/plans
    if (segments[2] === 'plans' && req.method === 'GET') {
      const plans = getPlansForRequest(user.id, requestId)
      sendWrapped(res, plans)
      return
    }

    if (req.method === 'GET') {
      const item = getTravelRequest(user.id, requestId)
      if (!item) {
        sendError(res, 404, 'Request not found')
        return
      }
      sendWrapped(res, item)
      return
    }

    if (req.method === 'PUT') {
      try {
        const patch = requireBody<Partial<TravelRequestInput>>(req.body)
        const updated = updateTravelRequest(user.id, requestId, patch)
        if (!updated) {
          sendError(res, 404, 'Request not found')
          return
        }
        sendWrapped(res, updated)
      } catch (e) {
        sendError(res, 400, e instanceof Error ? e.message : 'Bad request')
      }
      return
    }

    if (req.method === 'DELETE') {
      const ok = deleteTravelRequest(user.id, requestId)
      if (!ok) {
        sendError(res, 404, 'Request not found')
        return
      }
      sendWrapped(res, { deleted: true })
      return
    }

    sendError(res, 405, 'Method not allowed')
    return
  }

  // /travel/plans/compare or /travel/plans/:planId
  if (segments[0] === 'plans') {
    if (segments[1] === 'compare' && req.method === 'POST') {
      const { plan_ids } = (req.body || {}) as { plan_ids?: string[] }
      if (!Array.isArray(plan_ids) || plan_ids.length === 0) {
        sendError(res, 400, 'plan_ids is required')
        return
      }
      sendWrapped(res, comparePlans(plan_ids))
      return
    }

    const planId = segments[1]
    if (planId && req.method === 'GET') {
      const plan = getPlan(planId)
      if (!plan) {
        sendError(res, 404, 'Plan not found')
        return
      }
      sendWrapped(res, plan)
      return
    }
  }

  sendError(res, 404, 'Not found')
}
