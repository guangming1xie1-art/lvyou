/**
 * API 端点配置
 */

export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    PROFILE: '/auth/profile',
  },

  // 旅游请求相关
  TRAVEL: {
    CREATE_REQUEST: '/travel/requests',
    GET_REQUEST: (id: string) => `/travel/requests/${id}`,
    LIST_REQUESTS: '/travel/requests',
    UPDATE_REQUEST: (id: string) => `/travel/requests/${id}`,
    DELETE_REQUEST: (id: string) => `/travel/requests/${id}`,
  },

  // 旅游方案相关
  PLANS: {
    GET_PLANS: (requestId: string) => `/travel/requests/${requestId}/plans`,
    GET_PLAN: (planId: string) => `/travel/plans/${planId}`,
    COMPARE_PLANS: '/travel/plans/compare',
  },

  // 景点美食相关
  ATTRACTIONS: {
    LIST: '/attractions',
    GET: (id: string) => `/attractions/${id}`,
    SEARCH: '/attractions/search',
  },

  RESTAURANTS: {
    LIST: '/restaurants',
    GET: (id: string) => `/restaurants/${id}`,
    SEARCH: '/restaurants/search',
  },

  // 订单相关
  ORDERS: {
    CREATE: '/orders',
    GET: (id: string) => `/orders/${id}`,
    LIST: '/orders',
    UPDATE: (id: string) => `/orders/${id}`,
    CANCEL: (id: string) => `/orders/${id}/cancel`,
    PAY: (id: string) => `/orders/${id}/pay`,
  },
}

export default API_ENDPOINTS
