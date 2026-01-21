import { attractions, flights, hotels, restaurants } from '../mocks'
import type {
  DbAgentTask,
  DbAttraction,
  DbOrder,
  DbRestaurant,
  DbTravelPlan,
  DbTravelRequest,
  DbUser,
  FlightInfo,
  HotelInfo,
  RefreshTokenRecord,
} from './types'
import { hashPassword } from '../utils/password'
import { uuid, nowIso } from '../utils/generators'

export interface MemoryDb {
  users: DbUser[]
  refresh_tokens: RefreshTokenRecord[]
  travel_requests: DbTravelRequest[]
  travel_plans: DbTravelPlan[]
  orders: DbOrder[]
  attractions: DbAttraction[]
  restaurants: DbRestaurant[]
  flights: FlightInfo[]
  hotels: HotelInfo[]
  tasks: DbAgentTask[]
}

declare global {
  // eslint-disable-next-line no-var
  var __MOCK_API_DB__: MemoryDb | undefined
}

export async function createDb(): Promise<MemoryDb> {
  // ✅ 为 test 账号生成密码哈希（密码: 123456）
  const testPasswordHash = await hashPassword('123456')

  return {
    users: [
      {
        id: uuid(),
        username: 'test',
        email: 'test@example.com',
        password_hash: testPasswordHash,
        is_active: true,
        created_at: nowIso(),
        last_login: null,
      }
    ],
    refresh_tokens: [],
    travel_requests: [],
    travel_plans: [],
    orders: [],
    attractions: attractions as DbAttraction[],
    restaurants: restaurants as DbRestaurant[],
    flights: flights as FlightInfo[],
    hotels: hotels as HotelInfo[],
    tasks: [],
  }
}

export const db: MemoryDb = global.__MOCK_API_DB__ ?? await createDb()

if (!global.__MOCK_API_DB__) {
  global.__MOCK_API_DB__ = db
}
