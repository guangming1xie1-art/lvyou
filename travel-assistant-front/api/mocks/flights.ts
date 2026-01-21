import type { FlightInfo } from '../models/types'
import { id, pickMany, pickOne, randomInt } from '../utils/generators'

const AIRLINES = ['中国国航', '中国东方航空', '中国南方航空', '海南航空', '厦门航空', '春秋航空']

const CITY_AIRPORTS: Array<{ city: string; airport: string }> = [
  { city: '北京', airport: '首都国际机场' },
  { city: '上海', airport: '浦东国际机场' },
  { city: '杭州', airport: '萧山国际机场' },
  { city: '西安', airport: '咸阳国际机场' },
  { city: '成都', airport: '天府国际机场' },
  { city: '广州', airport: '白云国际机场' },
  { city: '深圳', airport: '宝安国际机场' },
]

const AMENITIES = ['WiFi', '机上餐食', 'USB 充电', '可选座位', '行李直挂', '影音娱乐']

function pad2(n: number): string {
  return `${n}`.padStart(2, '0')
}

function timeFromMinutes(totalMinutes: number): string {
  const h = Math.floor(totalMinutes / 60) % 24
  const m = totalMinutes % 60
  return `${pad2(h)}:${pad2(m)}`
}

export function generateFlights(count = 120): FlightInfo[] {
  const flights: FlightInfo[] = []

  for (let i = 0; i < count; i += 1) {
    const from = pickOne(CITY_AIRPORTS)
    let to = pickOne(CITY_AIRPORTS)
    while (to.city === from.city) to = pickOne(CITY_AIRPORTS)

    const airline = pickOne(AIRLINES)
    const flight_number = `${airline.includes('春秋') ? '9C' : 'MU'}${randomInt(1000, 9999)}`

    const depMinutes = randomInt(6 * 60, 22 * 60)
    const durationMin = randomInt(90, 240)
    const arrMinutes = depMinutes + durationMin

    flights.push({
      id: id('flt'),
      airline,
      flight_number,
      departure: {
        airport: from.airport,
        city: from.city,
        time: timeFromMinutes(depMinutes),
        date: '2026-01-01',
      },
      arrival: {
        airport: to.airport,
        city: to.city,
        time: timeFromMinutes(arrMinutes),
        date: '2026-01-01',
      },
      duration: `${Math.floor(durationMin / 60)}h${durationMin % 60}m`,
      stops: randomInt(0, 1),
      price: randomInt(450, 3200),
      cabin_class: pickOne(['economy', 'premium', 'business']),
      baggage: pickOne(['20kg', '23kg', '30kg']),
      amenities: pickMany(AMENITIES, randomInt(2, 5)),
    })
  }

  return flights
}

export const flights = generateFlights()
