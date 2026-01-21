import type { NextApiRequest, NextApiResponse } from 'next'
import { sendError, sendWrapped } from '../utils/response'
import { asString, parsePagination } from '../utils/validators'
import { getAttraction, getRestaurant, listAttractions, listRestaurants, searchAttractions, searchRestaurants } from '../models/attraction'

function paginate<T>(all: T[], page: number, page_size: number) {
  const start = (page - 1) * page_size
  const items = all.slice(start, start + page_size)
  return {
    items,
    total: all.length,
    page,
    page_size,
    total_pages: Math.ceil(all.length / page_size) || 1,
  }
}

export async function handleAttractionsRoute(req: NextApiRequest, res: NextApiResponse, segments: string[]): Promise<void> {
  const root = segments[0]

  if (root === 'attractions') {
    if (segments[1] === 'search' && req.method === 'GET') {
      const destination = asString(req.query.destination)
      const keyword = asString(req.query.keyword) || undefined
      const { page, page_size } = parsePagination(req.query as any)
      const results = searchAttractions({ destination: destination || undefined, keyword })
      sendWrapped(res, paginate(results, page, page_size))
      return
    }

    const id = segments[1]
    if (!id) {
      if (req.method !== 'GET') {
        sendError(res, 405, 'Method not allowed')
        return
      }
      const destination = asString(req.query.destination)
      const { page, page_size } = parsePagination(req.query as any)
      const results = listAttractions(destination || undefined)
      sendWrapped(res, paginate(results, page, page_size))
      return
    }

    if (req.method === 'GET') {
      const item = getAttraction(id)
      if (!item) {
        sendError(res, 404, 'Attraction not found')
        return
      }
      sendWrapped(res, item)
      return
    }

    sendError(res, 405, 'Method not allowed')
    return
  }

  if (root === 'restaurants') {
    if (segments[1] === 'search' && req.method === 'GET') {
      const destination = asString(req.query.destination)
      const keyword = asString(req.query.keyword) || undefined
      const cuisine_type = asString(req.query.cuisine_type) || undefined
      const { page, page_size } = parsePagination(req.query as any)
      const results = searchRestaurants({ destination: destination || undefined, keyword, cuisine_type })
      sendWrapped(res, paginate(results, page, page_size))
      return
    }

    const id = segments[1]
    if (!id) {
      if (req.method !== 'GET') {
        sendError(res, 405, 'Method not allowed')
        return
      }
      const destination = asString(req.query.destination)
      const { page, page_size } = parsePagination(req.query as any)
      const results = listRestaurants(destination || undefined)
      sendWrapped(res, paginate(results, page, page_size))
      return
    }

    if (req.method === 'GET') {
      const item = getRestaurant(id)
      if (!item) {
        sendError(res, 404, 'Restaurant not found')
        return
      }
      sendWrapped(res, item)
      return
    }

    sendError(res, 405, 'Method not allowed')
    return
  }

  sendError(res, 404, 'Not found')
}
