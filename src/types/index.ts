// 用户相关类型
export interface User {
  id: string
  name: string
  email: string
  phone?: string
  created_at?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  name: string
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  token: string
}

// 旅游请求相关类型
export interface TravelRequest {
  destination: string
  departure_date: string
  return_date: string
  people_count: number
  budget: number
  is_domestic: boolean
  preferences?: string[]
  special_requirements?: string
}

export interface TravelRequestWithId extends TravelRequest {
  request_id: string
  user_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
}

// 日程相关类型
export interface DailyItinerary {
  day: number
  date: string
  activities: Activity[]
  meals: Meal[]
  accommodation: Accommodation
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

// 费用明细类型
export interface CostBreakdown {
  transportation: number
  accommodation: number
  meals: number
  attractions: number
  other: number
  total: number
}

// 旅游方案类型
export interface TravelPlan {
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

// 景点美食类型
export interface Attraction {
  id: string
  name: string
  description: string
  location: string
  rating: number
  opening_hours: string
  ticket_price: number
  estimated_duration: number
  photos?: string[]
  tags: string[]
}

export interface Restaurant {
  id: string
  name: string
  cuisine_type: string
  rating: number
  price_range: string
  address: string
  specialties: string[]
  photos?: string[]
}

// 订单相关类型
export interface Order {
  order_id: string
  user_id: string
  plan_id: string
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed'
  total_amount: number
  payment_status: 'unpaid' | 'paid' | 'refunded'
  contact_name: string
  contact_phone: string
  contact_email: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface CreateOrderRequest {
  plan_id: string
  contact_name: string
  contact_phone: string
  contact_email: string
  notes?: string
}

// API 响应类型
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 错误类型
export interface ApiError {
  code: number
  message: string
  details?: unknown
}
