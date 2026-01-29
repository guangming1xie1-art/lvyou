package com.travelassistant.gateway.mcp;

import com.travelassistant.gateway.mcp.model.ToolDefinition;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.util.*;
import java.util.stream.Collectors;

/**
 * MCP 工具注册表
 * 管理所有可用的 MCP 工具定义
 */
@Slf4j
@Component
public class MCPToolRegistry {

    private final Map<String, ToolDefinition> tools = new HashMap<>();

    /**
     * 初始化并注册所有工具
     */
    @PostConstruct
    public void initialize() {
        log.info("Initializing MCP tool registry...");

        // 酒店服务工具
        registerTool(searchHotelsTool());
        registerTool(getHotelDetailsTool());

        // 航班服务工具
        registerTool(searchFlightsTool());
        registerTool(getFlightDetailsTool());

        // 景点服务工具
        registerTool(searchAttractionsTool());
        registerTool(getAttractionDetailsTool());

        // 预订服务工具
        registerTool(createBookingTool());
        registerTool(getBookingStatusTool());

        // 推荐服务工具
        registerTool(getRecommendationsTool());
        registerTool(getHotelRecommendationsTool());

        log.info("MCP tool registry initialized with {} tools", tools.size());
    }

    /**
     * 注册单个工具
     */
    private void registerTool(ToolDefinition tool) {
        tools.put(tool.getId(), tool);
        log.debug("Registered MCP tool: {} -> {}", tool.getId(), tool.getEndpoint());
    }

    /**
     * 获取所有工具
     */
    public List<ToolDefinition> getAllTools() {
        return new ArrayList<>(tools.values());
    }

    /**
     * 根据工具名获取工具定义
     */
    public ToolDefinition getTool(String toolName) {
        return tools.get(toolName);
    }

    /**
     * 检查工具是否存在
     */
    public boolean hasTool(String toolName) {
        return tools.containsKey(toolName);
    }

    // ==================== 工具定义 ====================

    /**
     * 搜索酒店工具
     * 使用 GET /api/hotel 并通过 query 参数过滤
     */
    private ToolDefinition searchHotelsTool() {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("description", "Search for hotels based on various criteria");

        Map<String, Object> properties = new HashMap<>();

        Map<String, Object> destination = new HashMap<>();
        destination.put("type", "string");
        destination.put("description", "Destination city or location");
        properties.put("destination", destination);

        Map<String, Object> minPrice = new HashMap<>();
        minPrice.put("type", "number");
        minPrice.put("description", "Minimum price per night");
        properties.put("min_price", minPrice);

        Map<String, Object> maxPrice = new HashMap<>();
        maxPrice.put("type", "number");
        maxPrice.put("description", "Maximum price per night");
        properties.put("max_price", maxPrice);

        Map<String, Object> minRating = new HashMap<>();
        minRating.put("type", "number");
        minRating.put("description", "Minimum hotel rating (0-5)");
        properties.put("min_rating", minRating);

        Map<String, Object> facility = new HashMap<>();
        facility.put("type", "string");
        facility.put("description", "Required facility (e.g., 'WiFi', 'Pool', 'Gym')");
        properties.put("facility", facility);

        schema.put("properties", properties);

        return ToolDefinition.builder()
                .id("search_hotels")
                .name("search_hotels")
                .description("Search for hotels with filters for destination, price range, rating, and facilities")
                .inputSchema(schema)
                .serviceName("hotel-service")
                .httpMethod("GET")
                .endpoint("/api/hotel")
                .paramMapping(Map.of(
                        "min_price", "minPrice",
                        "max_price", "maxPrice",
                        "min_rating", "minRating"
                ))
                .build();
    }

    /**
     * 获取酒店详情工具
     */
    private ToolDefinition getHotelDetailsTool() {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("description", "Get detailed information about a specific hotel");

        Map<String, Object> properties = new HashMap<>();

        Map<String, Object> id = new HashMap<>();
        id.put("type", "string");
        id.put("description", "Hotel ID");
        properties.put("id", id);

        schema.put("properties", properties);
        schema.put("required", List.of("id"));

        return ToolDefinition.builder()
                .id("get_hotel_details")
                .name("get_hotel_details")
                .description("Get detailed information about a specific hotel by ID")
                .inputSchema(schema)
                .serviceName("hotel-service")
                .httpMethod("GET")
                .endpoint("/api/hotel/{id}")
                .build();
    }

    /**
     * 搜索航班工具
     */
    private ToolDefinition searchFlightsTool() {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("description", "Search for flights based on route, date, and other criteria");

        Map<String, Object> properties = new HashMap<>();

        Map<String, Object> origin = new HashMap<>();
        origin.put("type", "string");
        origin.put("description", "Origin city or airport code");
        properties.put("origin", origin);

        Map<String, Object> destination = new HashMap<>();
        destination.put("type", "string");
        destination.put("description", "Destination city or airport code");
        properties.put("destination", destination);

        Map<String, Object> departureDate = new HashMap<>();
        departureDate.put("type", "string");
        departureDate.put("description", "Departure date (YYYY-MM-DD format)");
        properties.put("departure_date", departureDate);

        Map<String, Object> minPrice = new HashMap<>();
        minPrice.put("type", "number");
        minPrice.put("description", "Minimum price");
        properties.put("min_price", minPrice);

        Map<String, Object> maxPrice = new HashMap<>();
        maxPrice.put("type", "number");
        maxPrice.put("description", "Maximum price");
        properties.put("max_price", maxPrice);

        Map<String, Object> airline = new HashMap<>();
        airline.put("type", "string");
        airline.put("description", "Airline name");
        properties.put("airline", airline);

        schema.put("properties", properties);

        return ToolDefinition.builder()
                .id("search_flights")
                .name("search_flights")
                .description("Search for flights with filters for origin, destination, date, price, and airline")
                .inputSchema(schema)
                .serviceName("flight-service")
                .httpMethod("GET")
                .endpoint("/api/flight")
                .paramMapping(Map.of(
                        "departure_date", "departureDate",
                        "min_price", "minPrice",
                        "max_price", "maxPrice"
                ))
                .build();
    }

    /**
     * 获取航班详情工具
     */
    private ToolDefinition getFlightDetailsTool() {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("description", "Get detailed information about a specific flight");

        Map<String, Object> properties = new HashMap<>();

        Map<String, Object> id = new HashMap<>();
        id.put("type", "string");
        id.put("description", "Flight ID");
        properties.put("id", id);

        schema.put("properties", properties);
        schema.put("required", List.of("id"));

        return ToolDefinition.builder()
                .id("get_flight_details")
                .name("get_flight_details")
                .description("Get detailed information about a specific flight by ID")
                .inputSchema(schema)
                .serviceName("flight-service")
                .httpMethod("GET")
                .endpoint("/api/flight/{id}")
                .build();
    }

    /**
     * 搜索景点工具
     */
    private ToolDefinition searchAttractionsTool() {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("description", "Search for attractions based on location, category, and rating");

        Map<String, Object> properties = new HashMap<>();

        Map<String, Object> destination = new HashMap<>();
        destination.put("type", "string");
        destination.put("description", "Destination city or location");
        properties.put("destination", destination);

        Map<String, Object> category = new HashMap<>();
        category.put("type", "string");
        category.put("description", "Attraction category (e.g., 'Museum', 'Park', 'Historical')");
        properties.put("category", category);

        Map<String, Object> minRating = new HashMap<>();
        minRating.put("type", "number");
        minRating.put("description", "Minimum attraction rating (0-5)");
        properties.put("min_rating", minRating);

        Map<String, Object> tags = new HashMap<>();
        tags.put("type", "array");
        tags.put("items", new HashMap<String, Object>() {{
            put("type", "string");
        }});
        tags.put("description", "List of tags to filter by");
        properties.put("tags", tags);

        schema.put("properties", properties);

        return ToolDefinition.builder()
                .id("search_attractions")
                .name("search_attractions")
                .description("Search for attractions with filters for destination, category, rating, and tags")
                .inputSchema(schema)
                .serviceName("attraction-service")
                .httpMethod("GET")
                .endpoint("/api/attraction")
                .paramMapping(Map.of(
                        "min_rating", "minRating"
                ))
                .build();
    }

    /**
     * 获取景点详情工具
     */
    private ToolDefinition getAttractionDetailsTool() {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("description", "Get detailed information about a specific attraction");

        Map<String, Object> properties = new HashMap<>();

        Map<String, Object> id = new HashMap<>();
        id.put("type", "string");
        id.put("description", "Attraction ID");
        properties.put("id", id);

        schema.put("properties", properties);
        schema.put("required", List.of("id"));

        return ToolDefinition.builder()
                .id("get_attraction_details")
                .name("get_attraction_details")
                .description("Get detailed information about a specific attraction by ID")
                .inputSchema(schema)
                .serviceName("attraction-service")
                .httpMethod("GET")
                .endpoint("/api/attraction/{id}")
                .build();
    }

    /**
     * 创建预订工具
     */
    private ToolDefinition createBookingTool() {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("description", "Create a new booking for hotels, flights, or attractions");

        Map<String, Object> properties = new HashMap<>();

        Map<String, Object> userId = new HashMap<>();
        userId.put("type", "string");
        userId.put("description", "User ID");
        properties.put("user_id", userId);

        Map<String, Object> bookingType = new HashMap<>();
        bookingType.put("type", "string");
        bookingType.put("description", "Booking type (HOTEL, FLIGHT, ATTRACTION)");
        properties.put("booking_type", bookingType);

        Map<String, Object> resourceId = new HashMap<>();
        resourceId.put("type", "string");
        resourceId.put("description", "ID of the hotel, flight, or attraction");
        properties.put("resource_id", resourceId);

        Map<String, Object> bookingDate = new HashMap<>();
        bookingDate.put("type", "string");
        bookingDate.put("description", "Booking date (YYYY-MM-DD format)");
        properties.put("booking_date", bookingDate);

        Map<String, Object> totalPrice = new HashMap<>();
        totalPrice.put("type", "number");
        totalPrice.put("description", "Total price");
        properties.put("total_price", totalPrice);

        Map<String, Object> notes = new HashMap<>();
        notes.put("type", "string");
        notes.put("description", "Additional notes");
        properties.put("notes", notes);

        schema.put("properties", properties);

        return ToolDefinition.builder()
                .id("create_booking")
                .name("create_booking")
                .description("Create a new booking for hotels, flights, or attractions")
                .inputSchema(schema)
                .serviceName("booking-service")
                .httpMethod("POST")
                .endpoint("/api/booking")
                .paramMapping(Map.of(
                        "user_id", "userId",
                        "booking_type", "bookingType",
                        "resource_id", "resourceId",
                        "booking_date", "bookingDate",
                        "total_price", "totalPrice"
                ))
                .build();
    }

    /**
     * 获取预订状态工具
     */
    private ToolDefinition getBookingStatusTool() {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("description", "Get booking status and details");

        Map<String, Object> properties = new HashMap<>();

        Map<String, Object> id = new HashMap<>();
        id.put("type", "string");
        id.put("description", "Booking ID");
        properties.put("id", id);

        schema.put("properties", properties);
        schema.put("required", List.of("id"));

        return ToolDefinition.builder()
                .id("get_booking_status")
                .name("get_booking_status")
                .description("Get the status and details of a specific booking")
                .inputSchema(schema)
                .serviceName("booking-service")
                .httpMethod("GET")
                .endpoint("/api/booking/{id}")
                .build();
    }

    /**
     * 获取综合推荐工具
     */
    private ToolDefinition getRecommendationsTool() {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("description", "Get comprehensive recommendations for a user");

        Map<String, Object> properties = new HashMap<>();

        Map<String, Object> userId = new HashMap<>();
        userId.put("type", "string");
        userId.put("description", "User ID");
        properties.put("user_id", userId);

        Map<String, Object> type = new HashMap<>();
        type.put("type", "string");
        type.put("description", "Recommendation type: hotels, flights, attractions, or comprehensive");
        type.put("enum", List.of("hotels", "flights", "attractions", "comprehensive"));
        properties.put("type", type);

        Map<String, Object> limit = new HashMap<>();
        limit.put("type", "number");
        limit.put("description", "Maximum number of recommendations to return");
        properties.put("limit", limit);

        schema.put("properties", properties);

        return ToolDefinition.builder()
                .id("get_recommendations")
                .name("get_recommendations")
                .description("Get personalized recommendations for hotels, flights, attractions, or comprehensive")
                .inputSchema(schema)
                .serviceName("recommendation-service")
                .httpMethod("GET")
                .endpoint("/api/recommendation/comprehensive/{userId}")
                .paramMapping(Map.of(
                        "user_id", "userId"
                ))
                .build();
    }

    /**
     * 获取酒店推荐工具
     */
    private ToolDefinition getHotelRecommendationsTool() {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("description", "Get personalized hotel recommendations");

        Map<String, Object> properties = new HashMap<>();

        Map<String, Object> userId = new HashMap<>();
        userId.put("type", "string");
        userId.put("description", "User ID");
        properties.put("user_id", userId);

        Map<String, Object> limit = new HashMap<>();
        limit.put("type", "number");
        limit.put("description", "Maximum number of recommendations to return");
        properties.put("limit", limit);

        schema.put("properties", properties);

        return ToolDefinition.builder()
                .id("get_hotel_recommendations")
                .name("get_hotel_recommendations")
                .description("Get personalized hotel recommendations based on user preferences")
                .inputSchema(schema)
                .serviceName("recommendation-service")
                .httpMethod("GET")
                .endpoint("/api/recommendation/hotels/{userId}")
                .paramMapping(Map.of(
                        "user_id", "userId"
                ))
                .build();
    }
}
