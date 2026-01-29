package com.travelassistant.gateway.mcp;

import com.travelassistant.gateway.mcp.model.ToolDefinition;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;

import java.util.HashMap;
import java.util.Map;

/**
 * MCP 工具路由器
 * 负责将 MCP 工具调用路由到 MicroserviceToolAdapter 中的具体实现
 *
 * 简化版本：只负责路由，实际调用委托给 MicroserviceToolAdapter
 */
@Slf4j
@Component
public class MCPToolRouter {

    private final MCPToolRegistry toolRegistry;
    private final MicroserviceToolAdapter microserviceToolAdapter;

    @Autowired
    public MCPToolRouter(
            MCPToolRegistry toolRegistry,
            MicroserviceToolAdapter microserviceToolAdapter) {
        this.toolRegistry = toolRegistry;
        this.microserviceToolAdapter = microserviceToolAdapter;
    }

    /**
     * 路由并调用工具
     *
     * @param toolName 工具名称
     * @param parameters 工具参数
     * @param authHeader Authorization header (用于转发到后端服务)
     * @return 调用结果
     */
    public Mono<Map<String, Object>> routeAndCall(
            String toolName,
            Map<String, Object> parameters,
            String authHeader) {

        // 1. 验证工具是否存在
        if (!toolRegistry.hasTool(toolName)) {
            log.warn("Tool not found: {}", toolName);
            return Mono.just(createErrorResponse("Tool not found: " + toolName));
        }

        log.info("Routing tool call: {}", toolName);

        // 2. 路由到对应的实现方法
        switch (toolName) {
            // 酒店服务
            case "search_hotels":
                return microserviceToolAdapter.searchHotels(parameters, authHeader);
            case "get_hotel_details":
                return microserviceToolAdapter.getHotelDetails(parameters, authHeader);

            // 航班服务
            case "search_flights":
                return microserviceToolAdapter.searchFlights(parameters, authHeader);
            case "get_flight_details":
                return microserviceToolAdapter.getFlightDetails(parameters, authHeader);

            // 景点服务
            case "search_attractions":
                return microserviceToolAdapter.searchAttractions(parameters, authHeader);
            case "get_attraction_details":
                return microserviceToolAdapter.getAttractionDetails(parameters, authHeader);

            // 预订服务
            case "create_booking":
                return microserviceToolAdapter.createBooking(parameters, authHeader);
            case "get_booking_status":
                return microserviceToolAdapter.getBookingStatus(parameters, authHeader);
            case "cancel_booking":
                return microserviceToolAdapter.cancelBooking(parameters, authHeader);

            // 推荐服务
            case "get_recommendations":
                return microserviceToolAdapter.getRecommendations(parameters, authHeader);
            case "get_hotel_recommendations":
                return microserviceToolAdapter.getHotelRecommendations(parameters, authHeader);

            default:
                log.error("Unknown tool: {}", toolName);
                return Mono.just(createErrorResponse("Unknown tool: " + toolName));
        }
    }

    /**
     * 创建成功响应（保留用于兼容性）
     */
    private Map<String, Object> createSuccessResponse(Object data) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", data);
        return response;
    }

    /**
     * 创建错误响应
     */
    private Map<String, Object> createErrorResponse(String error) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("error", error);
        return response;
    }
}
