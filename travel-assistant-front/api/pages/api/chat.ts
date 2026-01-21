import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { delay, randomInt } from '@/lib/utils/generators'
import { pickOne } from '@/lib/utils/generators'

interface ChatBody {
  message: string
  conversation_id?: string
}

interface ChatResponse {
  response: string
  conversation_id?: string
  status: string
}

export default withMiddleware(
  requireAuth(async (req, res) => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
      const { message, conversation_id } = req.body as ChatBody

      if (!message) {
        return res.status(400).json({ error: 'Message is required' })
      }

      // Simulate AI processing delay
      await delay(randomInt(200, 600))

      // Generate mock AI response
      const responses = [
        `关于"${message}"，我建议您考虑以下几个方面：`,
        `根据您的需求"${message}"，我可以为您提供一些建议：`,
        `我理解您想了解"${message}"，让我为您整理一下：`,
      ]

      const mockResponse = {
        response: `${pickOne(responses)}`,
        conversation_id: conversation_id || `conv_${randomInt(1000, 9999)}`,
        status: 'ok',
        additional_data: {
          suggestions: [
            '您还可以问我关于特定目的地的信息',
            '需要我帮您规划行程吗？',
            '有什么特别想了解的景点或美食吗？',
          ],
        },
      }

      return res.status(200).json(mockResponse)
    } catch (error) {
      console.error('Chat API error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)