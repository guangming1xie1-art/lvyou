import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { createTravelRequest, listTravelRequests, generatePlans } from '@/lib/models/travel'
import type { DbTravelRequest, TravelRequestInput } from '@/lib/models/types'

interface CreateRequestBody extends TravelRequestInput {
  preferences?: string[]
  special_requirements?: string
}

interface CreateResponse {
  request: DbTravelRequest
  plans: any[]
}

export default withMiddleware(
  requireAuth(async (req, res) => {
    try {
      if (req.method === 'GET') {
        const page = parseInt(req.query.page as string) || 1
        const pageSize = parseInt(req.query.page_size as string) || 10
        const status = req.query.status as string

        const result = listTravelRequests(req.userId!, page, pageSize, status)
        return res.status(200).json(result)
      }

      if (req.method === 'POST') {
        const {
          destination,
          departure_date,
          return_date,
          people_count,
          budget,
          is_domestic,
          preferences,
          special_requirements,
        } = req.body as CreateRequestBody

        if (!destination || !departure_date || !return_date || !people_count || !budget) {
          return res.status(400).json({ error: 'Missing required fields' })
        }

        // 创建旅游请求
        const travelRequest = await createTravelRequest({
          user_id: req.userId!,
          destination,
          departure_date,
          return_date,
          people_count,
          budget,
          is_domestic,
          preferences,
          special_requirements,
        })

        // 自动生成方案
        const plans = generatePlans(travelRequest)

        const response: CreateResponse = {
          request: travelRequest,
          plans,
        }

        return res.status(201).json(response)
      }

      return res.status(405).json({ error: 'Method not allowed' })
    } catch (error) {
      console.error('Travel request error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)