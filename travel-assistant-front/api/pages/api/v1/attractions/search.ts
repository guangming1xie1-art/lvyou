import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { searchAttractions } from '@/lib/routes/attractions'

export default withMiddleware(async (req, res) => {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const destination = req.query.destination as string
    const keyword = req.query.keyword as string
    const page = parseInt(req.query.page as string) || 1
    const pageSize = parseInt(req.query.page_size as string) || 10

    if (!destination && !keyword) {
      return res.status(400).json({ error: 'destination or keyword parameter is required' })
    }

    const result = searchAttractions(destination || '', keyword || '', page, pageSize)
    
    return res.status(200).json(result)
  } catch (error) {
    console.error('Search attractions error:', error)
    return res.status(500).json({ error: 'Internal server error' })
  }
})