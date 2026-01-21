import type { NextApiRequest, NextApiResponse } from 'next'
import { applyCors, handlePreflight } from '../../lib/middlewares/cors'
import { handleAuthRoute } from '../../lib/routes/auth'
import { handleTravelRoute } from '../../lib/routes/travel'
import { handleAttractionsRoute } from '../../lib/routes/attractions'
import { handleOrdersRoute } from '../../lib/routes/orders'
import { handleAgentRoute, handleChatRoute } from '../../lib/routes/agent'

function getSegments(req: NextApiRequest): string[] {
  const slug = req.query.slug
  if (!slug) return []
  if (Array.isArray(slug)) return slug.map(String)
  return [String(slug)]
}

function debugEnabled(): boolean {
  return process.env.MOCK_API_DEBUG === 'true' || process.env.DEBUG_MOCK_API === 'true'
}

export default async function handler(req: NextApiRequest, res: NextApiResponse): Promise<void> {
  applyCors(req, res)
  if (handlePreflight(req, res)) return

  const segments = getSegments(req)

  if (debugEnabled()) {
    // eslint-disable-next-line no-console
    console.log(`[mock-api] ${req.method} /api/${segments.join('/')}`)
  }

  // /api/auth/*
  if (segments[0] === 'auth') {
    await handleAuthRoute(req, res, segments.slice(1))
    return
  }

  // /api/chat (rewritten from /chat)
  if (segments[0] === 'chat') {
    await handleChatRoute(req, res)
    return
  }

  // /api/agent/*
  if (segments[0] === 'agent') {
    await handleAgentRoute(req, res, segments)
    return
  }

  // /api/v1/*
  if (segments[0] === 'v1') {
    const resource = segments[1]

    if (resource === 'travel') {
      await handleTravelRoute(req, res, segments.slice(2))
      return
    }

    if (resource === 'orders') {
      await handleOrdersRoute(req, res, segments.slice(1))
      return
    }

    if (resource === 'attractions' || resource === 'restaurants') {
      await handleAttractionsRoute(req, res, segments.slice(1))
      return
    }

    if (resource === 'agent') {
      await handleAgentRoute(req, res, segments.slice(1))
      return
    }

    res.status(404).json({ detail: 'Not found' })
    return
  }

  res.status(404).json({ detail: 'Not found' })
}

export const config = {
  api: {
    bodyParser: true,
  },
}
