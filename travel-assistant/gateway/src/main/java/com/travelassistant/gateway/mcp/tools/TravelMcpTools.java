package com.travelassistant.gateway.mcp.tools;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Travel MCP Tools
 * 实现标准 MCP 协议工具，使用 Spring AI MCP Server
 * 通过 WebClient 负载均衡转发到各个微服务
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class TravelMcpTools {

    private final WebClient.Builder webClientBuilder;

    // ==================== 酒店工具 ====================

    /**
     * 搜索酒店
     */
    @Tool(name = "search_hotels", description = "搜索酒店，支持目的地、日期、价格和评分过滤")
    public Map<String, Object> searchHotels(
            @ToolParam(description = "目的地城市") String destination,
            @ToolParam(description = "入住日期 YYYY-MM-DD") String checkIn,
            @ToolParam(description = "离店日期 YYYY-MM-DD") String checkOut,
            @ToolParam(description = "最低价格", required = false) Double minPrice,
            @ToolParam(description = "最高价格", required = false) Double maxPrice,
            @ToolParam(description = "最低评分 0-5", required = false) Double minRating,
            @ToolParam(description = "设施需求", required = false) String facility) {

        log.debug("Searching hotels for destination: {}, checkIn: {}, checkOut: {}",
                destination, checkIn, checkOut);

        try {
            List<Map<String, Object>> hotels = webClientBuilder.build()
                    .get()
                    .uri("lb://hotel-service/api/hotel", uriBuilder -> {
                        uriBuilder.queryParam("destination", destination)
                                .queryParam("checkIn", checkIn)
                                .queryParam("checkOut", checkOut);
                        if (minPrice != null) uriBuilder.queryParam("minPrice", minPrice);
                        if (maxPrice != null) uriBuilder.queryParam("maxPrice", maxPrice);
                        if (minRating != null) uriBuilder.queryParam("minRating", minRating);
                        if (facility != null && !facility.isEmpty()) uriBuilder.queryParam("facility", facility);
                        return uriBuilder.build();
                    })
                    .retrieve()
//                    .bodyToMono(Map.class)
                    .bodyToMono(LIST_MAP_TYPE)
                    .block();
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", hotels);
            return response;
        } catch (Exception e) {
            log.error("search_hotels failed: {}", e.getMessage(), e);
            return createErrorResponse("搜索酒店失败: " + e.getMessage());
        }
    }

    /**
     * 获取酒店详情
     */
    @Tool(name = "get_hotel_details", description = "获取酒店详细信息")
    public Map<String, Object> getHotelDetails(
            @ToolParam(description = "酒店ID") String id) {

        log.debug("Getting hotel details for id: {}", id);

        try {
            return webClientBuilder.build()
                    .get()
                    .uri("lb://hotel-service/api/hotel/{id}", id)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            log.error("get_hotel_details failed: {}", e.getMessage(), e);
            return createErrorResponse("获取酒店详情失败: " + e.getMessage());
        }
    }

    // ==================== 航班工具 ====================
    private static final ParameterizedTypeReference<List<Map<String, Object>>> LIST_MAP_TYPE =
            new ParameterizedTypeReference<List<Map<String, Object>>>() {};
    /**
     * 搜索航班
     */
    @Tool(name = "search_flights", description = "搜索航班，支持航线、日期、价格和航空公司过滤")
    public Map<String, Object> searchFlights(
            @ToolParam(description = "出发地") String origin,
            @ToolParam(description = "目的地") String destination,
            @ToolParam(description = "出发日期 YYYY-MM-DD") String departureDate,
            @ToolParam(description = "最低价格", required = false) Double minPrice,
            @ToolParam(description = "最高价格", required = false) Double maxPrice,
            @ToolParam(description = "航空公司", required = false) String airline) {

        log.debug("Searching flights from {} to {} on {}", origin, destination, departureDate);

        try {
            List<Map<String, Object>> hotels = webClientBuilder.build()
                    .get()
                    .uri("lb://flight-service/api/flight", uriBuilder -> {
                        uriBuilder.queryParam("origin", origin)
                                .queryParam("destination", destination)
                                .queryParam("departureDate", departureDate);
                        if (minPrice != null) uriBuilder.queryParam("minPrice", minPrice);
                        if (maxPrice != null) uriBuilder.queryParam("maxPrice", maxPrice);
                        if (airline != null && !airline.isEmpty()) uriBuilder.queryParam("airline", airline);
                        return uriBuilder.build();
                    })
                    .retrieve()
//                    .bodyToMono(Map.class)
                    .bodyToMono(LIST_MAP_TYPE)
                    .block();
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", hotels);
            return response;
        } catch (Exception e) {
            log.error("search_flights failed: {}", e.getMessage(), e);
            return createErrorResponse("搜索航班失败: " + e.getMessage());
        }
    }

    /**
     * 获取航班详情
     */
    @Tool(name = "get_flight_details", description = "获取航班详细信息")
    public Map<String, Object> getFlightDetails(
            @ToolParam(description = "航班ID") String id) {

        log.debug("Getting flight details for id: {}", id);

        try {
            return webClientBuilder.build()
                    .get()
                    .uri("lb://flight-service/api/flight/{id}", id)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            log.error("get_flight_details failed: {}", e.getMessage(), e);
            return createErrorResponse("获取航班详情失败: " + e.getMessage());
        }
    }

    // ==================== 景点工具 ====================

    /**
     * 搜索景点
     */
    @Tool(name = "search_attractions", description = "搜索景点，支持目的地、分类、评分和标签过滤")
    public Map<String, Object> searchAttractions(
            @ToolParam(description = "目的地城市") String destination,
            @ToolParam(description = "景点分类", required = false) String category,
            @ToolParam(description = "最低评分 0-5", required = false) Double minRating,
            @ToolParam(description = "标签列表", required = false) List<String> tags) {

        log.debug("Searching attractions for destination: {}", destination);

        try {
            return webClientBuilder.build()
                    .get()
                    .uri("lb://attraction-service/api/attraction", uriBuilder -> {
                        uriBuilder.queryParam("destination", destination);
                        if (category != null && !category.isEmpty()) uriBuilder.queryParam("category", category);
                        if (minRating != null) uriBuilder.queryParam("minRating", minRating);
                        if (tags != null && !tags.isEmpty()) {
                            tags.forEach(tag -> uriBuilder.queryParam("tags", tag));
                        }
                        return uriBuilder.build();
                    })
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            log.error("search_attractions failed: {}", e.getMessage(), e);
            return createErrorResponse("搜索景点失败: " + e.getMessage());
        }
    }

    /**
     * 获取景点详情
     */
    @Tool(name = "get_attraction_details", description = "获取景点详细信息")
    public Map<String, Object> getAttractionDetails(
            @ToolParam(description = "景点ID") String id) {

        log.debug("Getting attraction details for id: {}", id);

        try {
            return webClientBuilder.build()
                    .get()
                    .uri("lb://attraction-service/api/attraction/{id}", id)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            log.error("get_attraction_details failed: {}", e.getMessage(), e);
            return createErrorResponse("获取景点详情失败: " + e.getMessage());
        }
    }

    // ==================== 预订工具 ====================

    /**
     * 创建预订
     */
    @Tool(name = "create_booking", description = "创建酒店、航班或景点预订")
    public Map<String, Object> createBooking(
            @ToolParam(description = "用户ID") String userId,
            @ToolParam(description = "预订类型 (HOTEL, FLIGHT, ATTRACTION)") String bookingType,
            @ToolParam(description = "资源ID (酒店/航班/景点ID)") String resourceId,
            @ToolParam(description = "预订日期 YYYY-MM-DD") String bookingDate,
            @ToolParam(description = "总价") Double totalPrice,
            @ToolParam(description = "备注", required = false) String notes) {

        log.debug("Creating booking for user: {}, type: {}, resource: {}", userId, bookingType, resourceId);

        try {
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("userId", userId);
            requestBody.put("bookingType", bookingType);
            requestBody.put("resourceId", resourceId);
            requestBody.put("bookingDate", bookingDate);
            requestBody.put("totalPrice", totalPrice);
            if (notes != null) requestBody.put("notes", notes);

            return webClientBuilder.build()
                    .post()
                    .uri("lb://booking-service/api/booking")
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            log.error("create_booking failed: {}", e.getMessage(), e);
            return createErrorResponse("创建预订失败: " + e.getMessage());
        }
    }

    /**
     * 获取预订状态
     */
    @Tool(name = "get_booking_status", description = "获取预订状态和详情")
    public Map<String, Object> getBookingStatus(
            @ToolParam(description = "预订ID") String id) {

        log.debug("Getting booking status for id: {}", id);

        try {
            return webClientBuilder.build()
                    .get()
                    .uri("lb://booking-service/api/booking/{id}", id)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            log.error("get_booking_status failed: {}", e.getMessage(), e);
            return createErrorResponse("获取预订状态失败: " + e.getMessage());
        }
    }

    // ==================== 推荐工具 ====================

    /**
     * 获取个性化推荐
     */
    @Tool(name = "get_recommendations", description = "获取个性化推荐（酒店、航班、景点或综合推荐）")
    public Map<String, Object> getRecommendations(
            @ToolParam(description = "用户ID") String userId,
            @ToolParam(description = "推荐类型 (hotels, flights, attractions, comprehensive)") String type,
            @ToolParam(description = "返回数量限制", required = false) Integer limit) {

        log.debug("Getting recommendations for user: {}, type: {}", userId, type);

        try {
            String baseUri;
            if ("hotels".equals(type)) {
                baseUri = "lb://recommendation-service/api/recommendation/hotels/{userId}";
            } else if ("flights".equals(type)) {
                baseUri = "lb://recommendation-service/api/recommendation/flights/{userId}";
            } else if ("attractions".equals(type)) {
                baseUri = "lb://recommendation-service/api/recommendation/attractions/{userId}";
            } else {
                baseUri = "lb://recommendation-service/api/recommendation/comprehensive/{userId}";
            }

            return webClientBuilder.build()
                    .get()
                    .uri(baseUri, uriBuilder -> {
                        if (limit != null) uriBuilder.queryParam("limit", limit);
                        return uriBuilder.build(userId);
                    })
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            log.error("get_recommendations failed: {}", e.getMessage(), e);
            return createErrorResponse("获取推荐失败: " + e.getMessage());
        }
    }

    // ==================== 辅助方法 ====================

    private Map<String, Object> createErrorResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("error", message);
        return response;
    }
}
