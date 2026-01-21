import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { delay, uuid, pickMany, nowIso } from '@/lib/utils/generators'
import { db } from '@/lib/models/db'
import type { FlightInfo, HotelInfo, DbAgentTask } from '@/lib/models/types'

interface SearchParams {
  origin: string
  destination: string
  departure_date: string
  return_date?: string
  passengers: number
  class?: string
}

export default withMiddleware(
  requireAuth(async (req, res) => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
      const params = req.body as SearchParams

      if (!params.origin || !params.destination || !params.departure_date || !params.passengers) {
        return res.status(400).json({ error: 'Missing required parameters' })
      }

      // Create task record
      const taskId = uuid()
      const task: DbAgentTask = {
        task_id: taskId,
        status: 'completed',
        result: null,
        created_at: nowIso(),
        updated_at: nowIso(),
        progress: 1.0,
      }

      // Simulate search
      await delay(800)

      // Generate mock results
      const outboundFlights = pickMany(db.flights, 8).map(f => ({
        ...f,
        departure: { ...f.departure, date: params.departure_date },
      }))

      let returnFlights: FlightInfo[] | undefined
      if (params.return_date) {
        returnFlights = pickMany(db.flights, 6).map(f => ({
          ...f,
          departure: { ...f.departure, date: params.return_date },
        }))
      }

      const hotels = pickMany(db.hotels, 10)

      db.tasks.unshift(task)

      return res.status(200).json({
        outbound_flights: outboundFlights,
        return_flights: returnFlights,
        hotels,
        task_id: taskId,
        search_metadata: {
          search_time: nowIso(),
          flights_count: outboundFlights.length + (returnFlights?.length || 0),
          hotels_count: hotels.length,
          currency: 'CNY',
        },
      })
    } catch (error) {
      console.error('Agent search error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)