import { db } from './db'
import type {
  DbTravelPlan,
  DbTravelRequest,
  TravelRequestInput,
  CostBreakdown,
  DailyItinerary,
  Activity,
  Meal,
  Accommodation,
} from './types'
import { nowIso, pickMany, pickOne, randomInt, uuid } from '../utils/generators'

function addDays(dateStr: string, days: number): string {
  const d = new Date(dateStr)
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

function toMoney(n: number): number {
  return Math.round(n * 100) / 100
}

function buildCostBreakdown(budget: number): CostBreakdown {
  const transportation = budget * randomInt(20, 35) / 100
  const accommodation = budget * randomInt(25, 40) / 100
  const meals = budget * randomInt(10, 20) / 100
  const attractions = budget * randomInt(5, 15) / 100
  const other = Math.max(budget - transportation - accommodation - meals - attractions, budget * 0.05)
  const total = transportation + accommodation + meals + attractions + other

  return {
    transportation: toMoney(transportation),
    accommodation: toMoney(accommodation),
    meals: toMoney(meals),
    attractions: toMoney(attractions),
    other: toMoney(other),
    total: toMoney(total),
  }
}

function destinationAttractions(destination: string) {
  return db.attractions.filter((a) => a.destination === destination)
}

function destinationRestaurants(destination: string) {
  return db.restaurants.filter((r) => r.destination === destination)
}

function destinationHotels(destination: string) {
  return db.hotels.filter((h) => h.location.includes(destination))
}

function buildDailyItinerary(destination: string, startDate: string, days: number): DailyItinerary[] {
  const atts = destinationAttractions(destination)
  const rests = destinationRestaurants(destination)
  const htls = destinationHotels(destination)

  const itinerary: DailyItinerary[] = []

  for (let day = 1; day <= days; day += 1) {
    const date = addDays(startDate, day - 1)
    const picks = atts.length ? pickMany(atts, randomInt(1, 2)) : []

    const activities: Activity[] = [
      {
        time: '09:00',
        title: picks[0]?.name || `${destination}城市漫步`,
        description: picks[0]?.description || '自由探索城市街区与地标。',
        location: picks[0]?.location || destination,
        duration: randomInt(2, 4),
        cost: picks[0]?.ticket_price ?? randomInt(0, 120),
        type: 'attraction',
      },
    ]

    if (picks[1]) {
      activities.push({
        time: '14:00',
        title: picks[1].name,
        description: picks[1].description,
        location: picks[1].location,
        duration: randomInt(2, 3),
        cost: picks[1].ticket_price,
        type: 'attraction',
      })
    } else {
      activities.push({
        time: '15:00',
        title: '咖啡/休闲时光',
        description: '在当地特色街区休息，品尝甜点或咖啡。',
        location: `${destination}·商圈`,
        duration: 2,
        cost: randomInt(30, 80),
        type: 'other',
      })
    }

    const mealRest = rests.length ? pickMany(rests, 2) : []

    const meals: Meal[] = [
      {
        type: 'breakfast',
        restaurant_name: '酒店早餐',
        cost: randomInt(20, 60),
      },
      {
        type: 'lunch',
        restaurant_name: mealRest[0]?.name || `${destination}特色餐馆`,
        cost: randomInt(60, 160),
        cuisine_type: mealRest[0]?.cuisine_type,
      },
      {
        type: 'dinner',
        restaurant_name: mealRest[1]?.name || `${destination}夜市小吃`,
        cost: randomInt(80, 220),
        cuisine_type: mealRest[1]?.cuisine_type,
      },
    ]

    const hotel = htls.length ? pickOne(htls) : null
    const accommodation: Accommodation = {
      hotel_name: hotel?.name || `${destination}精选酒店`,
      address: hotel?.location || `${destination}市中心`,
      check_in: date,
      check_out: addDays(date, 1),
      cost: hotel ? hotel.price_per_night : randomInt(300, 900),
      rating: hotel?.rating,
    }

    itinerary.push({
      day,
      date,
      activities,
      meals,
      accommodation,
    })
  }

  return itinerary
}

export function createTravelRequest(userId: string, input: TravelRequestInput): DbTravelRequest {
  const request: DbTravelRequest = {
    ...input,
    request_id: uuid(),
    user_id: userId,
    status: 'completed',
    created_at: nowIso(),
  }

  db.travel_requests.push(request)

  const planCount = randomInt(3, 5)
  const tripDays = randomInt(7, 10)

  for (let i = 0; i < planCount; i += 1) {
    const costBreakdown = buildCostBreakdown(input.budget)
    const daily_itinerary = buildDailyItinerary(input.destination, input.departure_date, tripDays)

    const plan: DbTravelPlan = {
      plan_id: uuid(),
      request_id: request.request_id,
      plan_name: `${input.destination}${tripDays}天${pickOne(['经典', '深度', '轻奢', '亲子', '美食'])}方案 ${i + 1}`,
      description: `包含 ${tripDays} 天游玩安排、住宿建议与费用明细，适合 ${input.people_count} 人出行。`,
      total_cost: costBreakdown.total,
      daily_itinerary,
      cost_breakdown: costBreakdown,
      highlights: pickMany(
        [
          '热门景点打卡 + 小众路线',
          '地道美食推荐',
          '交通衔接更顺畅',
          '住宿位置更优',
          '适合拍照的路线安排',
        ],
        randomInt(3, 4)
      ),
      notes: input.special_requirements ? `特殊需求：${input.special_requirements}` : undefined,
      created_at: nowIso(),
    }

    db.travel_plans.push(plan)
  }

  return request
}

export function listTravelRequests(userId: string): DbTravelRequest[] {
  return db.travel_requests.filter((r) => r.user_id === userId)
}

export function getTravelRequest(userId: string, requestId: string): DbTravelRequest | undefined {
  return db.travel_requests.find((r) => r.user_id === userId && r.request_id === requestId)
}

export function updateTravelRequest(userId: string, requestId: string, patch: Partial<TravelRequestInput>): DbTravelRequest | undefined {
  const req = getTravelRequest(userId, requestId)
  if (!req) return undefined
  Object.assign(req, patch)
  return req
}

export function deleteTravelRequest(userId: string, requestId: string): boolean {
  const idx = db.travel_requests.findIndex((r) => r.user_id === userId && r.request_id === requestId)
  if (idx === -1) return false
  db.travel_requests.splice(idx, 1)
  db.travel_plans = db.travel_plans.filter((p) => p.request_id !== requestId)
  return true
}

export function getPlansForRequest(userId: string, requestId: string): DbTravelPlan[] {
  const req = getTravelRequest(userId, requestId)
  if (!req) return []
  return db.travel_plans.filter((p) => p.request_id === requestId)
}

export function getPlan(planId: string): DbTravelPlan | undefined {
  return db.travel_plans.find((p) => p.plan_id === planId)
}

export function comparePlans(planIds: string[]): DbTravelPlan[] {
  const set = new Set(planIds)
  return db.travel_plans.filter((p) => set.has(p.plan_id))
}
