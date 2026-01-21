import type { HotelInfo } from '../models/types'
import { id, pickMany, pickOne, randomInt } from '../utils/generators'

const CITIES = ['北京', '上海', '杭州', '西安', '成都', '广州', '深圳']

const AMENITIES = ['免费 WiFi', '健身房', '游泳池', '早餐', '接机服务', '自助洗衣', '会议室', '亲子设施']

const DESCRIPTIONS = [
  '地理位置优越，交通便利，适合商务与休闲出行。',
  '房间宽敞舒适，服务贴心，周边美食丰富。',
  '设计感十足，配套设施完善，步行可达热门景点。',
]

export function generateHotels(count = 60): HotelInfo[] {
  const hotels: HotelInfo[] = []

  for (let i = 0; i < count; i += 1) {
    const city = pickOne(CITIES)
    const rating = Math.round((randomInt(30, 50) / 10) * 10) / 10

    hotels.push({
      id: id('htl'),
      name: `${city}${pickOne(['悦享', '臻选', '云端', '雅致', '拾光', '景致'])}酒店 ${randomInt(1, 99)}号店`,
      location: `${city}·${pickOne(['市中心', '西湖周边', '古城', '高新区', '火车站'])}`,
      rating,
      price_per_night: randomInt(280, 1600),
      amenities: pickMany(AMENITIES, randomInt(3, 7)),
      images: [
        `https://picsum.photos/seed/${city}-hotel-${i}/640/480`,
        `https://picsum.photos/seed/${city}-hotel-${i}-2/640/480`,
      ],
      description: pickOne(DESCRIPTIONS),
      check_in_time: '14:00',
      check_out_time: '12:00',
    })
  }

  return hotels
}

export const hotels = generateHotels()
