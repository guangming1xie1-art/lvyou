import { http } from '@/utils/request'
import type {
  TravelRequest,
  TravelRequestWithId,
  TravelPlan,
  Attraction,
  Restaurant,
  Order,
  CreateOrderRequest,
  PaginatedResponse,
} from '@/types'
import { API_ENDPOINTS } from './api'

/**
 * 旅游服务
 */
export const travelService = {
  /**
   * 创建旅游请求
   */
  createRequest: async (data: TravelRequest): Promise<TravelRequestWithId> => {
    return await http.post<TravelRequestWithId>(API_ENDPOINTS.TRAVEL.CREATE_REQUEST, data)
  },

  /**
   * 获取旅游请求详情
   */
  getRequest: async (requestId: string): Promise<TravelRequestWithId> => {
    return await http.get<TravelRequestWithId>(API_ENDPOINTS.TRAVEL.GET_REQUEST(requestId))
  },

  /**
   * 获取用户的旅游请求列表
   */
  listRequests: async (params?: {
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<TravelRequestWithId>> => {
    return await http.get<PaginatedResponse<TravelRequestWithId>>(
      API_ENDPOINTS.TRAVEL.LIST_REQUESTS,
      { params }
    )
  },

  /**
   * 获取旅游方案列表
   */
  getPlans: async (requestId: string): Promise<TravelPlan[]> => {
    return await http.get<TravelPlan[]>(API_ENDPOINTS.PLANS.GET_PLANS(requestId))
  },

  /**
   * 获取旅游方案详情
   */
  getPlanDetail: async (planId: string): Promise<TravelPlan> => {
    return await http.get<TravelPlan>(API_ENDPOINTS.PLANS.GET_PLAN(planId))
  },

  /**
   * 比较多个旅游方案
   */
  comparePlans: async (planIds: string[]): Promise<TravelPlan[]> => {
    return await http.post<TravelPlan[]>(API_ENDPOINTS.PLANS.COMPARE_PLANS, { plan_ids: planIds })
  },

  /**
   * 搜索景点
   */
  searchAttractions: async (params: {
    destination: string
    keyword?: string
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Attraction>> => {
    return await http.get<PaginatedResponse<Attraction>>(API_ENDPOINTS.ATTRACTIONS.SEARCH, {
      params,
    })
  },

  /**
   * 获取景点详情
   */
  getAttraction: async (id: string): Promise<Attraction> => {
    return await http.get<Attraction>(API_ENDPOINTS.ATTRACTIONS.GET(id))
  },

  /**
   * 搜索餐厅
   */
  searchRestaurants: async (params: {
    destination: string
    keyword?: string
    cuisine_type?: string
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Restaurant>> => {
    return await http.get<PaginatedResponse<Restaurant>>(API_ENDPOINTS.RESTAURANTS.SEARCH, {
      params,
    })
  },

  /**
   * 获取餐厅详情
   */
  getRestaurant: async (id: string): Promise<Restaurant> => {
    return await http.get<Restaurant>(API_ENDPOINTS.RESTAURANTS.GET(id))
  },

  /**
   * 创建订单
   */
  createOrder: async (data: CreateOrderRequest): Promise<Order> => {
    return await http.post<Order>(API_ENDPOINTS.ORDERS.CREATE, data)
  },

  /**
   * 获取订单详情
   */
  getOrder: async (orderId: string): Promise<Order> => {
    return await http.get<Order>(API_ENDPOINTS.ORDERS.GET(orderId))
  },

  /**
   * 获取订单列表
   */
  listOrders: async (params?: {
    status?: string
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Order>> => {
    return await http.get<PaginatedResponse<Order>>(API_ENDPOINTS.ORDERS.LIST, { params })
  },

  /**
   * 取消订单
   */
  cancelOrder: async (orderId: string): Promise<Order> => {
    return await http.post<Order>(API_ENDPOINTS.ORDERS.CANCEL(orderId))
  },

  /**
   * 支付订单
   */
  payOrder: async (orderId: string, paymentMethod: string): Promise<{ payment_url: string }> => {
    return await http.post<{ payment_url: string }>(API_ENDPOINTS.ORDERS.PAY(orderId), {
      payment_method: paymentMethod,
    })
  },
}
