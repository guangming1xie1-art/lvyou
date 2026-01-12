/**
 * Agent API 相关的类型定义
 * 基于 REST API 层的 schema 定义
 */

// 基础类型
export interface ErrorDetail {
  code: string
  message: string
  status_code?: number
}

export interface ErrorResponse {
  error: ErrorDetail
}

// 搜索相关类型
export interface SearchRequest {
  origin: string
  destination: string
  departure_date: string
  passengers: number
  return_date?: string
  cabin_class?: string
  trip_type?: 'one-way' | 'round-trip'
  check_in_date?: string
  check_out_date?: string
  rooms?: number
  min_rating?: number
  include_hotels?: boolean
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

export interface SearchMetadata {
  search_time: string
  flights_count: number
  hotels_count: number
  currency: string
}

export interface SearchResponse {
  outbound_flights: FlightInfo[]
  return_flights?: FlightInfo[]
  hotels: HotelInfo[]
  search_metadata: SearchMetadata
  task_id: string
  error?: ErrorDetail
}

// 推荐相关类型
export interface RecommendRequest {
  destination: string
  start_date: string
  end_date: string
  preferences?: string[]
  include_attractions?: boolean
  include_weather?: boolean
  include_reviews?: boolean
  max_attractions?: number
  attraction_category?: string
}

export interface DestinationInfo {
  name: string
  country: string
  region: string
  best_time_to_visit: string
  average_cost: string
  description: string
  highlights: string[]
  timezone: string
  language: string
  currency: string
}

export interface AttractionInfo {
  id: string
  name: string
  category: string
  description: string
  rating: number
  location: string
  opening_hours: string
  estimated_duration: string
  entrance_fee: string
  best_time_to_visit: string
  must_see: boolean
  images: string[]
  tips: string[]
}

export interface WeatherDay {
  date: string
  day_of_week: string
  temperature_high: number
  temperature_low: number
  condition: string
  humidity: number
  precipitation_chance: number
  wind_speed: number
  uv_index: number
  packing_recommendations: string[]
}

export interface ReviewSummary {
  total_reviews: number
  average_rating: number
  rating_distribution: {
    5: number
    4: number
    3: number
    2: number
    1: number
  }
  sentiment_breakdown: {
    positive: number
    neutral: number
    negative: number
  }
  pros: string[]
  cons: string[]
  recommended_by: number
}

export interface RecommendResponse {
  destination_info: DestinationInfo
  attractions: AttractionInfo[]
  weather_forecast: WeatherDay[]
  reviews: ReviewSummary
  task_id: string
  error?: ErrorDetail
}

// 预订相关类型
export interface PassengerInfo {
  first_name: string
  last_name: string
  date_of_birth: string
  passport_number?: string
  nationality?: string
  dietary_requirements?: string
}

export interface CustomerInfo {
  name: string
  email: string
  phone: string
  address?: string
}

export interface TripDetails {
  destination: string
  departure_date: string
  return_date?: string
  travelers: number
  trip_type: 'one-way' | 'round-trip'
  cabin_class?: string
}

export interface SelectedFlight {
  id: string
  flight_number: string
  price: number
  passengers: number
}

export interface SelectedHotel {
  id: string
  name: string
  check_in: string
  check_out: string
  rooms: number
  guests: number
  price_per_night: number
  total_nights: number
}

export interface AdditionalService {
  type: string
  name: string
  price: number
  quantity: number
}

export interface BookRequest {
  customer_info: CustomerInfo
  trip_details: TripDetails
  selected_flight?: SelectedFlight
  selected_hotel?: SelectedHotel
  passengers: PassengerInfo[]
  additional_services?: AdditionalService[]
  special_requests?: string
}

export interface PriceBreakdown {
  flights: number
  accommodation: number
  services: number
  taxes: number
  fees: number
  total: number
  currency: string
}

export interface TripSummary {
  destination: string
  departure_date: string
  return_date?: string
  travelers: number
  flight_details?: string
  hotel_details?: string
  total_duration?: string
}

export interface BookResponse {
  booking_id: string
  status: 'pending' | 'confirmed' | 'failed'
  confirmation_number: string
  price_breakdown: PriceBreakdown
  trip_summary: TripSummary
  next_steps: string[]
  task_id: string
  error?: ErrorDetail
}

// 任务状态相关类型
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface TaskInfo {
  task_id: string
  status: TaskStatus
  result?: unknown
  error?: ErrorDetail
  created_at: string
  updated_at: string
  progress: number // 0.0 to 1.0
}

export interface StatusResponse {
  task_id: string
  status: TaskStatus
  result?: unknown
  error?: ErrorDetail
  created_at: string
  updated_at: string
  progress: number
}

export interface TaskListResponse {
  total: number
  filtered: number
  tasks: TaskInfo[]
}

// API 基础配置
export interface ApiConfig {
  baseURL: string
  timeout: number
  retries: number
}

// WebSocket 相关类型（可选）
export interface WebSocketConfig {
  url: string
  reconnectInterval: number
  maxReconnectAttempts: number
}

export interface TaskUpdateMessage {
  type: 'task_update'
  data: {
    task_id: string
    status: TaskStatus
    progress: number
    result?: unknown
    error?: ErrorDetail
  }
}

// 通用 API 响应包装器
export interface ApiResponseWrapper<T> {
  data?: T
  error?: ErrorDetail
  metadata?: {
    task_id?: string
    timestamp: string
  }
}