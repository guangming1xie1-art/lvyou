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

export function createDb(): MemoryDb {
  return {
    users: [],
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

export const db: MemoryDb = global.__MOCK_API_DB__ ?? createDb()

if (!global.__MOCK_API_DB__) {
  global.__MOCK_API_DB__ = db
}
