import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'

interface HealthResponse {
  status: string
  timestamp: string
  version: string
}

export default withMiddleware((req, res) => {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const response: HealthResponse = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
    }

    return res.status(200).json(response)
  } catch (error) {
    console.error('Health check error:', error)
    return res.status(500).json({ error: 'Health check failed' })
  }
})