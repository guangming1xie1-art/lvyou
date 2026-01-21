import type { NextApiRequest, NextApiResponse } from 'next'
import { withMiddleware } from '@/lib/middlewares/withMiddleware'
import { requireAuth } from '@/lib/middlewares/requireAuth'
import { delay, uuid, pickMany, pickOne, nowIso, randomInt } from '@/lib/utils/generators'
import { db } from '@/lib/models/db'
import type { DbAgentTask } from '@/lib/models/types'

interface RecommendParams {
  destination: string
  dates: string[]
  people_count: number
  interests?: string[]
  budget_range?: {
    min: number
    max: number
  }
}

export default withMiddleware(
  requireAuth(async (req, res) => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
      const params = req.body as RecommendParams

      if (!params.destination || !params.dates || !params.people_count) {
        return res.status(400).json({ error: 'Missing required parameters' })
      }

      // Create task record
      const taskId = uuid()
      const task: DbAgentTask = {
        task_id: taskId,
        status: 'processing',
        created_at: nowIso(),
        updated_at: nowIso(),
        progress: 0.5,
      }

      // Simulate recommendation processing
      await delay(700)

      const destination = params.destination
      const attractions = db.attractions.filter(a => a.destination.includes(destination))
      const recommendedAttractions = pickMany(attractions.length ? attractions : db.attractions, 6).map(a => ({
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

      const weatherForecast = params.dates.slice(0, 5).map((date, idx) => ({
        date,
        day_of_week: pickOne(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']),
        temperature_high: randomInt(18, 32),
        temperature_low: randomInt(8, 18),
        condition: pickOne(['Sunny', 'Cloudy', 'Rainy', 'Overcast']),
        humidity: randomInt(40, 80),
        precipitation_chance: randomInt(0, 60),
        wind_speed: randomInt(1, 8),
        uv_index: randomInt(1, 10),
        packing_recommendations: pickMany(['舒适步行鞋', '防晒霜', '轻便雨伞', '薄外套'], 2),
      }))

      updateTask(task, {
        status: 'completed',
        progress: 1.0,
        result: {
          destination_info: {
            name: destination,
            country: '中国',
            region: '华东/华北/西南',
            best_time_to_visit: pickOne(['春秋季', '春季', '秋季', '全年']),
            average_cost: params.budget_range 
              ? `¥${params.budget_range.min}-¥${params.budget_range.max}/人`
              : pickOne(['¥3000-¥5000/人', '¥5000-¥8000/人', '¥8000+/人']),
            description: `${destination} 适合周末短途与深度旅行，兼具人文景观与城市体验。`,
            highlights: pickMany(['城市地标', '特色美食', '历史文化', '夜生活', '自然风光'], 4),
            timezone: 'Asia/Shanghai',
            language: '中文',
            currency: 'CNY',
          },
          attractions: recommendedAttractions,
          weather_forecast: weatherForecast,
          reviews: {
            total_reviews: randomInt(800, 5000),
            average_rating: 4.6,
            rating_distribution: { 5: 72, 4: 20, 3: 6, 2: 1, 1: 1 },
            sentiment_breakdown: { positive: 80, neutral: 15, negative: 5 },
            pros: ['交通便利', '体验丰富', '美食选择多'],
            cons: ['旺季人流较多', '部分景点需预约'],
            recommended_by: 92,
          },
        },
        updated_at: nowIso(),
      })

      db.tasks.unshift(task)

      return res.status(200).json({
        task_id: taskId,
        ...task.result,
      })
    } catch (error) {
      console.error('Agent recommend error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  })
)