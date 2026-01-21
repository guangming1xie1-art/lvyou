import type { DbRestaurant } from '../models/types'
import { id, pickMany, pickOne, randomInt } from '../utils/generators'

const CITY_CUISINES: Record<string, string[]> = {
  北京: ['京菜', '烤鸭', '火锅', '家常菜'],
  上海: ['本帮菜', '生煎', '海鲜', '江浙菜'],
  杭州: ['杭帮菜', '江浙菜', '茶点'],
  西安: ['陕西菜', '面食', '小吃'],
  成都: ['川菜', '火锅', '串串', '小吃'],
}

const SPECIALTIES = ['招牌菜', '必点菜', '特色小吃', '当季限定', '经典套餐']

export function generateRestaurants(count = 40): DbRestaurant[] {
  const destinations = Object.keys(CITY_CUISINES)
  const list: DbRestaurant[] = []

  for (let i = 0; i < count; i += 1) {
    const destination = pickOne(destinations)
    const cuisine_type = pickOne(CITY_CUISINES[destination])

    list.push({
      id: id('rst'),
      destination,
      name: `${destination}${pickOne(['老字号', '小馆', '食府', '私房菜', '味道'])}${randomInt(1, 99)}`, 
      cuisine_type,
      rating: Math.round((randomInt(36, 50) / 10) * 10) / 10,
      price_range: pickOne(['¥', '¥¥', '¥¥¥']),
      address: `${destination}${pickOne(['市中心', '古街', '商圈', '巷子口'])}${randomInt(1, 200)}号`,
      specialties: pickMany(SPECIALTIES, randomInt(2, 4)).map((s) => `${cuisine_type}${s}`),
      photos: [`https://picsum.photos/seed/${destination}-food-${i}/800/600`],
    })
  }

  return list
}

export const restaurants = generateRestaurants()
