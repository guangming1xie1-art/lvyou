export interface PublicUser {
  id: string
  username: string
  email: string
  is_active: boolean
  created_at: string
  last_login: string | null
}

export interface DbUser extends PublicUser {
  password_hash: string
}

export interface RefreshTokenRecord {
  token: string
  user_id: string
  created_at: string
  expires_at: string
  revoked: boolean
  replaced_by?: string
}

export type TravelRequestStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface TravelRequestInput {
  destination: string
  departure_date: string
  return_date: string
  people_count: number
  budget: number
  is_domestic: boolean
  preferences?: string[]
  special_requirements?: string
}

export interface DbTravelRequest extends TravelRequestInput {
  request_id: string
  user_id: string
  status: TravelRequestStatus
  created_at: string
}

export interface Activity {
  time: string
  title: string
  description: string
  location: string
  duration: number
  cost: number
  type: 'attraction' | 'transportation' | 'other'
}

export interface Meal {
  type: 'breakfast' | 'lunch' | 'dinner'
  restaurant_name: string
  cost: number
  cuisine_type?: string
}

export interface Accommodation {
  hotel_name: string
  address: string
  check_in: string
  check_out: string
  cost: number
  rating?: number
}

export interface DailyItinerary {
  day: number
  date: string
  activities: Activity[]
  meals: Meal[]
  accommodation: Accommodation
}

export interface CostBreakdown {
  transportation: number
  accommodation: number
  meals: number
  attractions: number
  other: number
  total: number
}

export interface DbTravelPlan {
  plan_id: string
  request_id: string
  plan_name: string
  description: string
  total_cost: number
  daily_itinerary: DailyItinerary[]
  cost_breakdown: CostBreakdown
  highlights: string[]
  notes?: string
  created_at: string
}

export interface DbAttraction {
  id: string
  destination: string
  name: string
  description: string
  location: string
  rating: number
  opening_hours: string
  ticket_price: number
  estimated_duration: number
  photos: string[]
  tags: string[]
}

export interface DbRestaurant {
  id: string
  destination: string
  name: string
  cuisine_type: string
  rating: number
  price_range: string
  address: string
  specialties: string[]
  photos: string[]
}

export type OrderStatus = 'pending' | 'confirmed' | 'cancelled' | 'completed'
export type PaymentStatus = 'unpaid' | 'paid' | 'refunded'

export interface DbOrder {
  order_id: string
  user_id: string
  plan_id: string
  status: OrderStatus
  total_amount: number
  payment_status: PaymentStatus
  contact_name: string
  contact_phone: string
  contact_email: string
  notes?: string
  created_at: string
  updated_at: string
}

export type AgentTaskStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface DbAgentTask {
  task_id: string
  status: AgentTaskStatus
  result?: unknown
  error?: { code: string; message: string; status_code?: number }
  created_at: string
  updated_at: string
  progress: number
}

export interface FlightInfo {
  id: string
  airline: string
  flight_number: string
  departure: {
    airport: string
    city: string
    time: string
    date: string
  }
  arrival: {
    airport: string
    city: string
    time: string
    date: string
  }
  duration: string
  stops: number
  price: number
  cabin_class: string
  baggage: string
  amenities: string[]
}

export interface HotelInfo {
  id: string
  name: string
  location: string
  rating: number
  price_per_night: number
  amenities: string[]
  images: string[]
  description: string
  check_in_time: string
  check_out_time: string
}
