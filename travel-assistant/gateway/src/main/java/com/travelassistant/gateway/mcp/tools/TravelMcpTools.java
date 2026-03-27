package com.travelassistant.gateway.mcp.tools;

import com.travelassistant.gateway.mcp.config.McpProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Component
@RequiredArgsConstructor
public class TravelMcpTools {

    private final WebClient.Builder webClientBuilder;
    private final McpProperties mcpProperties;

    private static final ParameterizedTypeReference<List<Map<String, Object>>> LIST_MAP_TYPE =
            new ParameterizedTypeReference<List<Map<String, Object>>>() {};
    
    private static final ParameterizedTypeReference<Map<String, Object>> MAP_TYPE =
            new ParameterizedTypeReference<Map<String, Object>>() {};

    @Tool(name = "search_hotels", description = "搜索酒店，支持目的地、日期、价格和评分过滤")
    public Map<String, Object> searchHotels(
            @ToolParam(description = "目的地城市") String destination,
            @ToolParam(description = "入住日期 YYYY-MM-DD") String checkIn,
            @ToolParam(description = "离店日期 YYYY-MM-DD") String checkOut,
            @ToolParam(description = "最低价格", required = false) Double minPrice,
            @ToolParam(description = "最高价格", required = false) Double maxPrice,
            @ToolParam(description = "最低评分 0-5", required = false) Double minRating,
            @ToolParam(description = "设施需求", required = false) String facility) {

        log.debug("Searching hotels for destination: {}, checkIn: {}, checkOut: {}", destination, checkIn, checkOut);

        McpProperties.ToolConfig config = mcpProperties.getTools().get("search-hotels");
        if (config == null || !config.isEnabled()) {
            return createErrorResponse("工具 search_hotels 未配置或已禁用");
        }

        try {
            Map<String, Object> params = new HashMap<>();
            params.put("destination", destination);
            params.put("checkInDate", checkIn);
            params.put("checkOutDate", checkOut);
            if (minPrice != null) params.put("minPrice", minPrice);
            if (maxPrice != null) params.put("maxPrice", maxPrice);
            if (minRating != null) params.put("minRating", minRating);
            if (facility != null && !facility.isEmpty()) params.put("facilities", facility);

            List<Map<String, Object>> hotels = executeGetRequest(config, params);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", hotels);
            return response;
        } catch (Exception e) {
            log.error("search_hotels failed: {}", e.getMessage(), e);
            return createErrorResponse("搜索酒店失败: " + e.getMessage());
        }
    }

    @Tool(name = "get_hotel_details", description = "获取酒店详细信息")
    public Map<String, Object> getHotelDetails(
            @ToolParam(description = "酒店ID") String id) {

        log.debug("Getting hotel details for id: {}", id);

        McpProperties.ToolConfig config = mcpProperties.getTools().get("get-hotel-details");
        if (config == null || !config.isEnabled()) {
            return createErrorResponse("工具 get_hotel_details 未配置或已禁用");
        }

        try {
            Map<String, Object> result = executeGetByIdRequest(config, id);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", result);
            return response;
        } catch (Exception e) {
            log.error("get_hotel_details failed: {}", e.getMessage(), e);
            return createErrorResponse("获取酒店详情失败: " + e.getMessage());
        }
    }

    @Tool(name = "search_flights", description = "搜索航班，支持航线、日期、价格和航空公司过滤")
    public Map<String, Object> searchFlights(
            @ToolParam(description = "出发地") String origin,
            @ToolParam(description = "目的地") String destination,
            @ToolParam(description = "出发日期 YYYY-MM-DD") String departureDate,
            @ToolParam(description = "最低价格", required = false) Double minPrice,
            @ToolParam(description = "最高价格", required = false) Double maxPrice,
            @ToolParam(description = "航空公司", required = false) String airline) {

        log.debug("Searching flights from {} to {} on {}", origin, destination, departureDate);

        McpProperties.ToolConfig config = mcpProperties.getTools().get("search-flights");
        if (config == null || !config.isEnabled()) {
            return createErrorResponse("工具 search_flights 未配置或已禁用");
        }

        try {
            Map<String, Object> params = new HashMap<>();
            params.put("origin", origin);
            params.put("destination", destination);
            params.put("departureDate", departureDate);
            if (minPrice != null) params.put("minPrice", minPrice);
            if (maxPrice != null) params.put("maxPrice", maxPrice);
            if (airline != null && !airline.isEmpty()) params.put("airline", airline);

            List<Map<String, Object>> flights = executePostRequest(config, params);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", flights);
            return response;
        } catch (Exception e) {
            log.error("search_flights failed: {}", e.getMessage(), e);
            return createErrorResponse("搜索航班失败: " + e.getMessage());
        }
    }

    @Tool(name = "get_flight_details", description = "获取航班详细信息")
    public Map<String, Object> getFlightDetails(
            @ToolParam(description = "航班ID") String id) {

        log.debug("Getting flight details for id: {}", id);

        McpProperties.ToolConfig config = mcpProperties.getTools().get("get-flight-details");
        if (config == null || !config.isEnabled()) {
            return createErrorResponse("工具 get_flight_details 未配置或已禁用");
        }

        try {
            Map<String, Object> result = executeGetByIdRequest(config, id);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", result);
            return response;
        } catch (Exception e) {
            log.error("get_flight_details failed: {}", e.getMessage(), e);
            return createErrorResponse("获取航班详情失败: " + e.getMessage());
        }
    }

    @Tool(name = "search_attractions", description = "搜索景点，支持目的地、分类、评分和标签过滤")
    public Map<String, Object> searchAttractions(
            @ToolParam(description = "目的地城市") String destination,
            @ToolParam(description = "景点分类", required = false) String category,
            @ToolParam(description = "最低评分 0-5", required = false) Double minRating,
            @ToolParam(description = "标签列表", required = false) List<String> tags) {

        log.debug("Searching attractions for destination: {}", destination);

        McpProperties.ToolConfig config = mcpProperties.getTools().get("search-attractions");
        if (config == null || !config.isEnabled()) {
            return createErrorResponse("工具 search_attractions 未配置或已禁用");
        }

        try {
            Map<String, Object> params = new HashMap<>();
            params.put("destination", destination);
            if (category != null && !category.isEmpty()) params.put("category", category);
            if (minRating != null) params.put("minRating", minRating);
            if (tags != null && !tags.isEmpty()) params.put("tags", tags);

            List<Map<String, Object>> attractions = executeGetRequest(config, params);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", attractions);
            return response;
        } catch (Exception e) {
            log.error("search_attractions failed: {}", e.getMessage(), e);
            return createErrorResponse("搜索景点失败: " + e.getMessage());
        }
    }

    @Tool(name = "get_attraction_details", description = "获取景点详细信息")
    public Map<String, Object> getAttractionDetails(
            @ToolParam(description = "景点ID") String id) {

        log.debug("Getting attraction details for id: {}", id);

        McpProperties.ToolConfig config = mcpProperties.getTools().get("get-attraction-details");
        if (config == null || !config.isEnabled()) {
            return createErrorResponse("工具 get_attraction_details 未配置或已禁用");
        }

        try {
            Map<String, Object> result = executeGetByIdRequest(config, id);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", result);
            return response;
        } catch (Exception e) {
            log.error("get_attraction_details failed: {}", e.getMessage(), e);
            return createErrorResponse("获取景点详情失败: " + e.getMessage());
        }
    }

    @Tool(name = "create_booking", description = "创建酒店、航班或景点预订")
    public Map<String, Object> createBooking(
            @ToolParam(description = "用户ID") String userId,
            @ToolParam(description = "预订类型 (HOTEL, FLIGHT, ATTRACTION)") String bookingType,
            @ToolParam(description = "资源ID (酒店/航班/景点ID)") String resourceId,
            @ToolParam(description = "预订日期 YYYY-MM-DD") String bookingDate,
            @ToolParam(description = "总价") Double totalPrice,
            @ToolParam(description = "备注", required = false) String notes) {

        log.debug("Creating booking for user: {}, type: {}, resource: {}", userId, bookingType, resourceId);

        McpProperties.ToolConfig config = mcpProperties.getTools().get("create-booking");
        if (config == null || !config.isEnabled()) {
            return createErrorResponse("工具 create_booking 未配置或已禁用");
        }

        try {
            Map<String, Object> body = new HashMap<>();
            body.put("userId", UUID.fromString(userId));
            body.put("bookingType", bookingType);
            body.put("resourceId", UUID.fromString(resourceId));
            body.put("bookingDate", LocalDateTime.parse(bookingDate + "T00:00:00"));
            body.put("totalPrice", BigDecimal.valueOf(totalPrice));
            if (notes != null) body.put("notes", notes);

            Map<String, Object> result = executePostRequestSingle(config, body);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", result);
            return response;
        } catch (Exception e) {
            log.error("create_booking failed: {}", e.getMessage(), e);
            return createErrorResponse("创建预订失败: " + e.getMessage());
        }
    }

    @Tool(name = "get_booking_status", description = "获取预订状态和详情")
    public Map<String, Object> getBookingStatus(
            @ToolParam(description = "预订ID") String id) {

        log.debug("Getting booking status for id: {}", id);

        McpProperties.ToolConfig config = mcpProperties.getTools().get("get-booking-status");
        if (config == null || !config.isEnabled()) {
            return createErrorResponse("工具 get_booking_status 未配置或已禁用");
        }

        try {
            Map<String, Object> result = executeGetByIdRequest(config, id);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", result);
            return response;
        } catch (Exception e) {
            log.error("get_booking_status failed: {}", e.getMessage(), e);
            return createErrorResponse("获取预订状态失败: " + e.getMessage());
        }
    }

    @Tool(name = "get_recommendations", description = "获取个性化推荐")
    public Map<String, Object> getRecommendations(
            @ToolParam(description = "用户ID") String userId,
            @ToolParam(description = "推荐类型 (hotels, flights, attractions, comprehensive)", required = false) String type,
            @ToolParam(description = "返回数量限制", required = false) Integer limit) {

        log.debug("Getting recommendations for user: {}, type: {}", userId, type);

        McpProperties.ToolConfig config = mcpProperties.getTools().get("get-recommendations");
        if (config == null || !config.isEnabled()) {
            return createErrorResponse("工具 get_recommendations 未配置或已禁用");
        }

        try {
            String path;
            if (type != null && !type.isEmpty()) {
                path = "/api/recommendation/" + type + "/" + UUID.fromString(userId);
            } else {
                path = config.getPath().replace("{userId}", UUID.fromString(userId).toString());
            }
            
            Map<String, Object> result = executeGetRequestWithPath(config, path, limit);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", result);
            return response;
        } catch (Exception e) {
            log.error("get_recommendations failed: {}", e.getMessage(), e);
            return createErrorResponse("获取推荐失败: " + e.getMessage());
        }
    }

    private List<Map<String, Object>> executeGetRequest(McpProperties.ToolConfig config, Map<String, Object> params) {
        return webClientBuilder.build()
                .get()
                .uri(uriBuilder -> {
                    uriBuilder.scheme("lb").host(config.getService()).path(config.getPath());
                    params.forEach((key, value) -> {
                        if (value != null) {
                            if (value instanceof List) {
                                uriBuilder.queryParam(key, ((List<?>) value).toArray());
                            } else {
                                uriBuilder.queryParam(key, value);
                            }
                        }
                    });
                    return uriBuilder.build();
                })
                .retrieve()
                .bodyToMono(LIST_MAP_TYPE)
                .block();
    }

    private Map<String, Object> executeGetByIdRequest(McpProperties.ToolConfig config, String id) {
        return webClientBuilder.build()
                .get()
                .uri(uriBuilder -> uriBuilder.scheme("lb").host(config.getService()).path(config.getPath()).build(id))
                .retrieve()
                .bodyToMono(MAP_TYPE)
                .block();
    }

    private Map<String, Object> executeGetRequestWithPath(McpProperties.ToolConfig config, String path, Integer limit) {
        return webClientBuilder.build()
                .get()
                .uri(uriBuilder -> {
                    uriBuilder.scheme("lb").host(config.getService()).path(path);
                    if (limit != null) uriBuilder.queryParam("limit", limit);
                    return uriBuilder.build();
                })
                .retrieve()
                .bodyToMono(MAP_TYPE)
                .block();
    }

    private List<Map<String, Object>> executePostRequest(McpProperties.ToolConfig config, Map<String, Object> body) {
        return webClientBuilder.build()
                .post()
                .uri(uriBuilder -> uriBuilder.scheme("lb").host(config.getService()).path(config.getPath()).build())
                .contentType(MediaType.APPLICATION_JSON)
                .body(BodyInserters.fromValue(body))
                .retrieve()
                .bodyToMono(LIST_MAP_TYPE)
                .block();
    }

    private Map<String, Object> executePostRequestSingle(McpProperties.ToolConfig config, Map<String, Object> body) {
        return webClientBuilder.build()
                .post()
                .uri(uriBuilder -> uriBuilder.scheme("lb").host(config.getService()).path(config.getPath()).build())
                .contentType(MediaType.APPLICATION_JSON)
                .body(BodyInserters.fromValue(body))
                .retrieve()
                .bodyToMono(MAP_TYPE)
                .block();
    }

    private Map<String, Object> createErrorResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("error", message);
        return response;
    }
}
