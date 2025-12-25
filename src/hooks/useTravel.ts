import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useTravelStore } from '@/store'
import { travelService } from '@/services/travelService'
import type { TravelRequest, CreateOrderRequest } from '@/types'

/**
 * 旅游相关的自定义 Hook
 */
export const useTravel = () => {
  const navigate = useNavigate()
  const { currentRequest, plans, selectedPlan, setCurrentRequest, setPlans, selectPlan } =
    useTravelStore()

  // 创建旅游请求
  const createRequestMutation = useMutation({
    mutationFn: (data: TravelRequest) => travelService.createRequest(data),
    onSuccess: (data) => {
      setCurrentRequest(data)
      navigate(`/plans?requestId=${data.request_id}`)
    },
  })

  // 获取旅游请求详情
  const useRequestQuery = (requestId?: string) => {
    return useQuery({
      queryKey: ['travel-request', requestId],
      queryFn: () => travelService.getRequest(requestId!),
      enabled: !!requestId,
    })
  }

  // 获取旅游方案列表
  const usePlansQuery = (requestId?: string) => {
    return useQuery({
      queryKey: ['travel-plans', requestId],
      queryFn: () => travelService.getPlans(requestId!),
      enabled: !!requestId,
      staleTime: 1000 * 60 * 5, // 5分钟
    })
  }

  // 获取旅游方案详情
  const usePlanDetailQuery = (planId?: string) => {
    return useQuery({
      queryKey: ['travel-plan', planId],
      queryFn: () => travelService.getPlanDetail(planId!),
      enabled: !!planId,
    })
  }

  // 搜索景点
  const useAttractionsQuery = (params: Parameters<typeof travelService.searchAttractions>[0]) => {
    return useQuery({
      queryKey: ['attractions', params],
      queryFn: () => travelService.searchAttractions(params),
      enabled: !!params.destination,
    })
  }

  // 搜索餐厅
  const useRestaurantsQuery = (params: Parameters<typeof travelService.searchRestaurants>[0]) => {
    return useQuery({
      queryKey: ['restaurants', params],
      queryFn: () => travelService.searchRestaurants(params),
      enabled: !!params.destination,
    })
  }

  // 创建订单
  const createOrderMutation = useMutation({
    mutationFn: (data: CreateOrderRequest) => travelService.createOrder(data),
    onSuccess: (data) => {
      navigate(`/orders/${data.order_id}`)
    },
  })

  // 获取订单详情
  const useOrderQuery = (orderId?: string) => {
    return useQuery({
      queryKey: ['order', orderId],
      queryFn: () => travelService.getOrder(orderId!),
      enabled: !!orderId,
    })
  }

  // 取消订单
  const cancelOrderMutation = useMutation({
    mutationFn: (orderId: string) => travelService.cancelOrder(orderId),
  })

  return {
    currentRequest,
    plans,
    selectedPlan,
    setCurrentRequest,
    setPlans,
    selectPlan,
    createRequest: createRequestMutation.mutate,
    createRequestAsync: createRequestMutation.mutateAsync,
    isCreatingRequest: createRequestMutation.isPending,
    createRequestError: createRequestMutation.error,
    useRequestQuery,
    usePlansQuery,
    usePlanDetailQuery,
    useAttractionsQuery,
    useRestaurantsQuery,
    createOrder: createOrderMutation.mutate,
    createOrderAsync: createOrderMutation.mutateAsync,
    isCreatingOrder: createOrderMutation.isPending,
    createOrderError: createOrderMutation.error,
    useOrderQuery,
    cancelOrder: cancelOrderMutation.mutate,
    isCancellingOrder: cancelOrderMutation.isPending,
  }
}
