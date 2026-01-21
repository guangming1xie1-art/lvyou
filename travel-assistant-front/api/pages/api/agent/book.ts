import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { delay, uuid, nowIso, randomInt } from '@/lib/utils/generators'
import { db } from '@/lib/models/db'
import type { DbAgentTask } from '@/lib/models/types'

interface BookParams {
  trip_details: {
    destination: string
    departure_date: string
    return_date?: string
    travelers: number
  }
  selected_flight?: {
    id: string
    price: number
  }
  selected_hotel?: {
    id: string
    price_per_night: number
    total_nights: number
    rooms?: number
  }
  additional_services?: Array<{
    id: string
    name: string
    price: number
    quantity: number
  }>
  passengers: Array<{
    first_name: string
    last_name: string
    passport?: string
    date_of_birth: string
  }>
  contact: {
    email: string
    phone: string
  }
}

interface BookResponse {
  booking_id: string
  status: string
  confirmation_number: string
  price_breakdown: {
    flights: number
    accommodation: number
    services: number
    taxes: number
    fees: number
    total: number
    currency: string
  }
  trip_summary: {
    destination: string
    departure_date: string
    return_date?: string
    travelers: number
    flight_details?: string
    hotel_details?: string
  }
  next_steps: string[]
}

export default withMiddleware(
  requireAuth(async (req, res) => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
      const params = req.body as BookParams

      if (!params.trip_details || !params.passengers || !params.contact) {
        return res.status(400).json({ error: 'Missing required booking parameters' })
      }

      // Create task record
      const taskId = uuid()
      const task: DbAgentTask = {
        task_id: taskId,
        status: 'processing',
        created_at: nowIso(),
        updated_at: nowIso(),
        progress: 0.4,
      }

      // Simulate booking processing
      await delay(900)

      // Generate booking result
      const bookingId = uuid()
      const confirmationNumber = `CNF-${randomInt(100000, 999999)}`
      
      const flightsCost = params.selected_flight?.price ? 
        Number(params.selected_flight.price) * params.passengers.length : 0
      
      const nights = params.selected_hotel?.total_nights || 0
      const accommodationCost = params.selected_hotel?.price_per_night ? 
        Number(params.selected_hotel.price_per_night) * nights * (params.selected_hotel.rooms || 1) : 0
      
      const servicesCost = Array.isArray(params.additional_services)
        ? params.additional_services.reduce((sum, s) => sum + Number(s.price || 0) * Number(s.quantity || 1), 0)
        : 0

      const taxes = Math.round((flightsCost + accommodationCost) * 0.08)
      const fees = 30
      const total = flightsCost + accommodationCost + servicesCost + taxes + fees

      const result: BookResponse = {
        booking_id: bookingId,
        status: 'confirmed',
        confirmation_number: confirmationNumber,
        price_breakdown: {
          flights: flightsCost,
          accommodation: accommodationCost,
          services: servicesCost,
          taxes,
          fees,
          total,
          currency: 'CNY',
        },
        trip_summary: {
          destination: params.trip_details.destination,
          departure_date: params.trip_details.departure_date,
          return_date: params.trip_details.return_date,
          travelers: params.passengers.length,
          flight_details: params.selected_flight ? `${params.selected_flight.id}` : undefined,
          hotel_details: params.selected_hotel ? `Hotel` : undefined,
        },
        next_steps: [
          '请确认乘机人信息',
          '出行当天请提前 2 小时到达机场',
          '如需发票可在订单页申请',
        ],
      }

      updateTask(task, {
        status: 'completed',
        progress: 1.0,
        result,
        updated_at: nowIso(),
      })

      db.tasks.unshift(task)

      return res.status(200).json({
        task_id: taskId,
        ...result,
      })
    } catch (error) {
      console.error('Agent book error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)