import type { NextApiRequest, NextApiResponse } from 'next'
import { db } from '../models/db'
import { requireAuth } from '../middlewares/auth'
import { sendError, sendWrapped } from '../utils/response'
import { delay, nowIso, pickMany, pickOne, randomInt, uuid } from '../utils/generators'
import type { DbAgentTask, FlightInfo, HotelInfo } from '../models/types'

function normalizeCity(city: string): string {
  const c = city.trim().toLowerCase()
  const map: Record<string, string> = {
    beijing: '北京',
    shanghai: '上海',
    hangzhou: '杭州',
    xian: '西安',
    xi’an: '西安',
    chengdu: '成都',
    guangzhou: '广州',
    shenzhen: '深圳',
  }
  return map[c] || city
}

function createTask(): DbAgentTask {
  const ts = nowIso()
  const task: DbAgentTask = {
    task_id: uuid(),
    status: 'pending',
    created_at: ts,
    updated_at: ts,
    progress: 0,
  }
  db.tasks.unshift(task)
  return task
}

function updateTask(task: DbAgentTask, patch: Partial<DbAgentTask>) {
  Object.assign(task, patch)
  task.updated_at = nowIso()
}

function setFlightDate(f: FlightInfo, date: string): FlightInfo {
  const dep = { ...f.departure, date }
  const arr = { ...f.arrival, date }
  return { ...f, departure: dep, arrival: arr }
}

function buildSearchResults(params: Record<string, any>): {
  outbound_flights: FlightInfo[]
  return_flights?: FlightInfo[]
  hotels: HotelInfo[]
  flights_count: number
  hotels_count: number
} {
  const origin = normalizeCity(String(params.origin || '北京'))
  const destination = normalizeCity(String(params.destination || '上海'))

  const flightPool = db.flights.filter((f) => f.departure.city.includes(origin) && f.arrival.city.includes(destination))
  const outboundRaw = flightPool.length ? pickMany(flightPool, Math.min(8, flightPool.length)) : pickMany(db.flights, 8)

  const outbound_flights = outboundRaw.map((f) => setFlightDate(f, String(params.departure_date || '2026-01-01')))

  let return_flights: FlightInfo[] | undefined
  if (params.return_date) {
    const returnPool = db.flights.filter((f) => f.departure.city.includes(destination) && f.arrival.city.includes(origin))
    const returnRaw = returnPool.length ? pickMany(returnPool, Math.min(6, returnPool.length)) : pickMany(db.flights, 6)
    return_flights = returnRaw.map((f) => setFlightDate(f, String(params.return_date)))
  }

  const hotelPool = db.hotels.filter((h) => h.location.includes(destination))
  const hotels = hotelPool.length ? pickMany(hotelPool, Math.min(10, hotelPool.length)) : pickMany(db.hotels, 10)

  return {
    outbound_flights,
    return_flights,
    hotels,
    flights_count: outbound_flights.length + (return_flights?.length || 0),
    hotels_count: hotels.length,
  }
}

function buildRecommendResult(params: Record<string, any>) {
  const destination = normalizeCity(String(params.destination || '北京'))
  const atts = db.attractions.filter((a) => a.destination === destination)

  const attractions = pickMany(atts.length ? atts : db.attractions, Math.min(6, atts.length || 6)).map((a) => ({
    id: a.id,
    name: a.name,
    category: pickOne(a.tags.length ? a.tags : ['热门']),
    description: a.description,
    rating: a.rating,
    location: a.location,
    opening_hours: a.opening_hours,
    estimated_duration: `${a.estimated_duration}小时`,
    entrance_fee: a.ticket_price ? `¥${a.ticket_price}` : '免费',
    best_time_to_visit: pickOne(['上午', '下午', '傍晚']),
    must_see: a.rating >= 4.6,
    images: a.photos,
    tips: pickMany(['建议提前预约', '建议避开周末高峰', '建议带上雨具', '可搭配附近美食街'], 2),
  }))

  const weather_forecast = Array.from({ length: 5 }).map((_, idx) => {
    const date = new Date(Date.now() + idx * 24 * 3600 * 1000)
    const d = date.toISOString().slice(0, 10)
    return {
      date: d,
      day_of_week: pickOne(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']),
      temperature_high: randomInt(18, 32),
      temperature_low: randomInt(8, 18),
      condition: pickOne(['Sunny', 'Cloudy', 'Rainy', 'Overcast']),
      humidity: randomInt(40, 80),
      precipitation_chance: randomInt(0, 60),
      wind_speed: randomInt(1, 8),
      uv_index: randomInt(1, 10),
      packing_recommendations: pickMany(['舒适步行鞋', '防晒霜', '轻便雨伞', '薄外套'], 2),
    }
  })

  return {
    destination_info: {
      name: destination,
      country: '中国',
      region: '华东/华北/西南',
      best_time_to_visit: pickOne(['春秋季', '春季', '秋季', '全年']),
      average_cost: pickOne(['¥3000-¥5000/人', '¥5000-¥8000/人', '¥8000+/人']),
      description: `${destination} 适合周末短途与深度旅行，兼具人文景观与城市体验。`,
      highlights: pickMany(['城市地标', '特色美食', '历史文化', '夜生活', '自然风光'], 4),
      timezone: 'Asia/Shanghai',
      language: '中文',
      currency: 'CNY',
    },
    attractions,
    weather_forecast,
    reviews: {
      total_reviews: randomInt(800, 5000),
      average_rating: 4.6,
      rating_distribution: { 5: 72, 4: 20, 3: 6, 2: 1, 1: 1 },
      sentiment_breakdown: { positive: 80, neutral: 15, negative: 5 },
      pros: ['交通便利', '体验丰富', '美食选择多'],
      cons: ['旺季人流较多', '部分景点需预约'],
      recommended_by: 92,
    },
  }
}

function buildBookResult(params: Record<string, any>) {
  const booking_id = uuid()
  const confirmation_number = `CNF-${randomInt(100000, 999999)}`
  const flight = params.selected_flight
  const hotel = params.selected_hotel

  const flightsCost = flight?.price ? Number(flight.price) * Number(flight.passengers || 1) : 0
  const nights = hotel?.total_nights ? Number(hotel.total_nights) : 0
  const accommodationCost = hotel?.price_per_night ? Number(hotel.price_per_night) * nights * Number(hotel.rooms || 1) : 0
  const servicesCost = Array.isArray(params.additional_services)
    ? params.additional_services.reduce((sum: number, s: any) => sum + Number(s.price || 0) * Number(s.quantity || 1), 0)
    : 0

  const taxes = Math.round((flightsCost + accommodationCost) * 0.08)
  const fees = 30
  const total = flightsCost + accommodationCost + servicesCost + taxes + fees

  return {
    booking_id,
    status: 'confirmed' as const,
    confirmation_number,
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
      destination: params.trip_details?.destination || '未知',
      departure_date: params.trip_details?.departure_date || '2026-01-01',
      return_date: params.trip_details?.return_date,
      travelers: params.trip_details?.travelers || params.passengers?.length || 1,
      flight_details: flight ? `${flight.flight_number}` : undefined,
      hotel_details: hotel ? `${hotel.name}` : undefined,
    },
    next_steps: ['请确认乘机人信息', '出行当天请提前 2 小时到达机场', '如需发票可在订单页申请'],
  }
}

export async function handleChatRoute(req: NextApiRequest, res: NextApiResponse): Promise<void> {
  if (req.method !== 'POST') {
    sendError(res, 405, 'Method not allowed')
    return
  }

  const message = String((req.body as any)?.message || '')
  await delay(randomInt(200, 600))

  sendWrapped(res, {
    search_results: [],
    recommendations: [],
    booking_info: {},
    response: `（Mock AI）我已收到：${message || '你好'}。你可以继续询问行程、景点或预订需求。`,
    status: 'ok',
  })
}

export async function handleAgentRoute(req: NextApiRequest, res: NextApiResponse, segments: string[]): Promise<void> {
  const user = requireAuth(req, res)
  if (!user) return

  const action = segments[1] || ''

  if (action === 'status' && req.method === 'GET') {
    const taskId = segments[2]
    if (!taskId) {
      sendWrapped(res, {
        service: 'mock-agent',
        status: 'ok',
        time: nowIso(),
      })
      return
    }

    const task = db.tasks.find((t) => t.task_id === taskId)
    if (!task) {
      sendError(res, 404, 'Task not found')
      return
    }
    sendWrapped(res, task)
    return
  }

  if (action === 'tasks' && req.method === 'GET') {
    const tasks = db.tasks.slice(0, 50)
    sendWrapped(res, {
      total: db.tasks.length,
      filtered: tasks.length,
      tasks,
    })
    return
  }

  if (action === 'chat' && req.method === 'POST') {
    const message = String((req.body as any)?.message || '')
    await delay(randomInt(200, 700))
    sendWrapped(res, {
      search_results: [],
      recommendations: [],
      booking_info: {},
      response: `（Mock AI）关于“${message || '你的问题'}”，我建议先确认出行时间与偏好，我可以帮你生成方案。`,
      status: 'ok',
    })
    return
  }

  if (action === 'search' && req.method === 'POST') {
    const task = createTask()
    updateTask(task, { status: 'processing', progress: 0.2 })

    await delay(randomInt(800, 1600))
    const result = buildSearchResults(req.body as any)
    updateTask(task, { status: 'completed', progress: 1, result })

    sendWrapped(res, {
      ...result,
      search_metadata: {
        search_time: nowIso(),
        flights_count: result.flights_count,
        hotels_count: result.hotels_count,
        currency: 'CNY',
      },
      task_id: task.task_id,
    })
    return
  }

  if (action === 'recommend' && req.method === 'POST') {
    const task = createTask()
    updateTask(task, { status: 'processing', progress: 0.3 })

    await delay(randomInt(700, 1400))
    const result = buildRecommendResult(req.body as any)
    updateTask(task, { status: 'completed', progress: 1, result })

    sendWrapped(res, { ...result, task_id: task.task_id })
    return
  }

  if (action === 'book' && req.method === 'POST') {
    const task = createTask()
    updateTask(task, { status: 'processing', progress: 0.4 })

    await delay(randomInt(900, 1700))
    const result = buildBookResult(req.body as any)
    updateTask(task, { status: 'completed', progress: 1, result })

    sendWrapped(res, { ...result, task_id: task.task_id })
    return
  }

  sendError(res, 404, 'Not found')
}
