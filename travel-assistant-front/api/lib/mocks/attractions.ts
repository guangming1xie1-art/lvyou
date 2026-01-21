import type { DbAttraction } from '../models/types'
import { id, pickMany, pickOne, randomInt } from '../utils/generators'

const CITY_TAGS: Record<string, string[]> = {
  北京: ['历史', '文化', '博物馆', '亲子', '地标'],
  上海: ['城市风光', '艺术', '购物', '地标'],
  杭州: ['自然', '湖景', '人文', '网红'],
  西安: ['历史', '古迹', '文化', '博物馆'],
  成都: ['美食', '休闲', '自然', '亲子'],
}

const ATTRACTION_NAMES: Record<string, string[]> = {
  北京: ['故宫博物院', '天坛公园', '颐和园', '八达岭长城', '南锣鼓巷'],
  上海: ['外滩', '东方明珠', '豫园', '上海博物馆', '田子坊'],
  杭州: ['西湖', '灵隐寺', '西溪湿地', '宋城', '龙井村'],
  西安: ['兵马俑', '大雁塔', '古城墙', '回民街', '陕西历史博物馆'],
  成都: ['大熊猫繁育研究基地', '宽窄巷子', '锦里', '都江堰', '青城山'],
}

export function generateAttractions(): DbAttraction[] {
  const list: DbAttraction[] = []

  for (const destination of Object.keys(ATTRACTION_NAMES)) {
    const names = ATTRACTION_NAMES[destination] || []
    for (const name of names) {
      const rating = Math.round((randomInt(40, 50) / 10) * 10) / 10
      const ticket_price = randomInt(0, 180)

      list.push({
        id: id('att'),
        destination,
        name,
        description: `${name} 是 ${destination} 的热门打卡地，适合拍照与深度体验。`,
        location: `${destination}${pickOne(['市中心', '景区入口', '古城区', '河畔'])}`,
        rating,
        opening_hours: pickOne(['09:00-17:00', '08:30-18:00', '全天开放']),
        ticket_price,
        estimated_duration: randomInt(1, 5),
        photos: [`https://picsum.photos/seed/${destination}-${name}/800/600`],
        tags: pickMany(CITY_TAGS[destination] || ['热门'], randomInt(2, 4)),
      })
    }
  }

  // Ensure 20+ entries by adding a few extras
  while (list.length < 25) {
    const destination = pickOne(Object.keys(ATTRACTION_NAMES))
    list.push({
      id: id('att'),
      destination,
      name: `${destination}城市公园 ${randomInt(1, 20)}`,
      description: '城市休闲好去处，适合散步与轻徒步。',
      location: `${destination}·公园区`,
      rating: Math.round((randomInt(35, 50) / 10) * 10) / 10,
      opening_hours: '全天开放',
      ticket_price: 0,
      estimated_duration: randomInt(1, 3),
      photos: [`https://picsum.photos/seed/${destination}-park-${list.length}/800/600`],
      tags: ['自然', '休闲'],
    })
  }

  return list
}

export const attractions = generateAttractions()
