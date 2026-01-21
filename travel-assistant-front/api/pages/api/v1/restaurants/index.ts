import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { listRestaurants } from '@/lib/routes/attractions'

export default withMiddleware(async (req, res) => {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const destination = req.query.destination as string
    const page = parseInt(req.query.page as string) || 1
    const pageSize = parseInt(req.query.page_size as string) || 10
    const cuisine = req.query.cuisine as string

    const result = listRestaurants(destination, cuisine, page, pageSize)
    
    return res.status(200).json(result)
  } catch (error) {
    console.error('List restaurants error:', error)
    return res.status(500).json({ error: 'Internal server error' })
  }
})