package com.travelassistant.gateway.mcp;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;

import java.util.*;

/**
 * MCP Tool Adapter for Microservices
 * 将后端微服务的 API 调用封装为标准的 MCP 工具
 *
 * 提供工具方法的实现，供 MCPToolRouter 调用
 * 支持 JWT 认证转发到后端服务
 */
@Slf4j
@Component
public class MicroserviceToolAdapter {

    private final WebClient.Builder webClientBuilder;

    public MicroserviceToolAdapter(WebClient.Builder webClientBuilder) {
        this.webClientBuilder = webClientBuilder;
    }

    // ==================== 工具实现 ====================

    /**
     * 搜索酒店
     */
    public Mono<Map<String, Object>> searchHotels(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "hotel-service",
            "/api/hotel",
            "GET",
            parameters,
            Map.of(
                "min_price", "minPrice",
                "max_price", "maxPrice",
                "min_rating", "minRating"
            ),
            authHeader
        );
    }

    /**
     * 获取酒店详情
     */
    public Mono<Map<String, Object>> getHotelDetails(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "hotel-service",
            "/api/hotel/{id}",
            "GET",
            parameters,
            null,
            authHeader
        );
    }

    /**
     * 搜索航班
     */
    public Mono<Map<String, Object>> searchFlights(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "flight-service",
            "/api/flight",
            "GET",
            parameters,
            Map.of(
                "departure_date", "departureDate",
                "min_price", "minPrice",
                "max_price", "maxPrice"
            ),
            authHeader
        );
    }

    /**
     * 获取航班详情
     */
    public Mono<Map<String, Object>> getFlightDetails(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "flight-service",
            "/api/flight/{id}",
            "GET",
            parameters,
            null,
            authHeader
        );
    }

    /**
     * 搜索景点
     */
    public Mono<Map<String, Object>> searchAttractions(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "attraction-service",
            "/api/attraction",
            "GET",
            parameters,
            Map.of(
                "min_rating", "minRating"
            ),
            authHeader
        );
    }

    /**
     * 获取景点详情
     */
    public Mono<Map<String, Object>> getAttractionDetails(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "attraction-service",
            "/api/attraction/{id}",
            "GET",
            parameters,
            null,
            authHeader
        );
    }

    /**
     * 创建预订
     */
    public Mono<Map<String, Object>> createBooking(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "booking-service",
            "/api/booking",
            "POST",
            parameters,
            Map.of(
                "user_id", "userId",
                "booking_type", "bookingType",
                "resource_id", "resourceId",
                "booking_date", "bookingDate",
                "total_price", "totalPrice"
            ),
            authHeader
        );
    }

    /**
     * 获取预订状态
     */
    public Mono<Map<String, Object>> getBookingStatus(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "booking-service",
            "/api/booking/{id}",
            "GET",
            parameters,
            null,
            authHeader
        );
    }

    /**
     * 取消预订
     */
    public Mono<Map<String, Object>> cancelBooking(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "booking-service",
            "/api/booking/{id}",
            "DELETE",
            parameters,
            null,
            authHeader
        );
    }

    /**
     * 获取综合推荐
     */
    public Mono<Map<String, Object>> getRecommendations(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "recommendation-service",
            "/api/recommendation/comprehensive/{userId}",
            "GET",
            parameters,
            Map.of(
                "user_id", "userId"
            ),
            authHeader
        );
    }

    /**
     * 获取酒店推荐
     */
    public Mono<Map<String, Object>> getHotelRecommendations(Map<String, Object> parameters, String authHeader) {
        return callMicroservice(
            "recommendation-service",
            "/api/recommendation/hotels/{userId}",
            "GET",
            parameters,
            Map.of(
                "user_id", "userId"
            ),
            authHeader
        );
    }

    // ==================== 通用微服务调用 ====================

    /**
     * 通用微服务调用方法
     *
     * @param serviceName 服务名称
     * @param endpoint API 端点
     * @param httpMethod HTTP 方法
     * @param parameters 请求参数
     * @param paramMapping 参数名映射（snake_case -> camelCase）
     * @param authHeader Authorization header（用于转发）
     * @return 响应结果
     */
    private Mono<Map<String, Object>> callMicroservice(
            String serviceName,
            String endpoint,
            String httpMethod,
            Map<String, Object> parameters,
            Map<String, String> paramMapping,
            String authHeader) {

        try {
            WebClient webClient = webClientBuilder
                    .baseUrl("lb://")
                    .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(10 * 1024 * 1024))
                    .build();

            // 转换参数
            Map<String, Object> convertedParams = convertParameters(parameters, paramMapping);

            // 处理路径参数
            String processedEndpoint = endpoint;
            Map<String, Object> queryParams = new HashMap<>(convertedParams);
            Map<String, Object> bodyParams = new HashMap<>(convertedParams);

            if (processedEndpoint.contains("{")) {
                for (Map.Entry<String, Object> entry : parameters.entrySet()) {
                    String placeholder = "{" + entry.getKey() + "}";
                    if (processedEndpoint.contains(placeholder)) {
                        processedEndpoint = processedEndpoint.replace(placeholder, String.valueOf(entry.getValue()));
                        queryParams.remove(entry.getKey());
                        bodyParams.remove(entry.getKey());
                    }
                }
            }

            // 根据 HTTP 方法调用
            Mono<Object> responseMono;

            switch (httpMethod.toUpperCase()) {
                case "GET":
                    responseMono = webClient
                            .get()
                            .uri(uriBuilder -> {
                                uriBuilder.path(serviceName + processedEndpoint);
                                queryParams.forEach(uriBuilder::queryParam);
                                return uriBuilder.build();
                            })
                            .accept(MediaType.APPLICATION_JSON)
                            .headers(headers -> {
                                if (authHeader != null && !authHeader.isEmpty()) {
                                    headers.set("Authorization", authHeader);
                                }
                            })
                            .retrieve()
                            .bodyToMono(Object.class);
                    break;

                case "POST":
                    responseMono = webClient
                            .post()
                            .uri(serviceName + processedEndpoint)
                            .contentType(MediaType.APPLICATION_JSON)
                            .accept(MediaType.APPLICATION_JSON)
                            .headers(headers -> {
                                if (authHeader != null && !authHeader.isEmpty()) {
                                    headers.set("Authorization", authHeader);
                                }
                            })
                            .body(BodyInserters.fromValue(bodyParams))
                            .retrieve()
                            .bodyToMono(Object.class);
                    break;

                case "PUT":
                    responseMono = webClient
                            .put()
                            .uri(serviceName + processedEndpoint)
                            .contentType(MediaType.APPLICATION_JSON)
                            .accept(MediaType.APPLICATION_JSON)
                            .headers(headers -> {
                                if (authHeader != null && !authHeader.isEmpty()) {
                                    headers.set("Authorization", authHeader);
                                }
                            })
                            .body(BodyInserters.fromValue(bodyParams))
                            .retrieve()
                            .bodyToMono(Object.class);
                    break;

                case "DELETE":
                    responseMono = webClient
                            .delete()
                            .uri(serviceName + processedEndpoint)
                            .accept(MediaType.APPLICATION_JSON)
                            .headers(headers -> {
                                if (authHeader != null && !authHeader.isEmpty()) {
                                    headers.set("Authorization", authHeader);
                                }
                            })
                            .retrieve()
                            .bodyToMono(Object.class);
                    break;

                default:
                    return Mono.just(createErrorResponse("Unsupported HTTP method: " + httpMethod));
            }

            // 返回异步结果
            return responseMono
                    .map(this::createSuccessResponse)
                    .onErrorResume(WebClientResponseException.class, ex -> {
                        log.error("Microservice call failed: {} {}, Status: {}, Body: {}",
                                serviceName, endpoint, ex.getStatusCode(), ex.getResponseBodyAsString());
                        return Mono.just(createErrorResponse("Service error: " + ex.getStatusCode() + " - " + ex.getMessage()));
                    })
                    .onErrorResume(Exception.class, ex -> {
                        log.error("Microservice call failed: {} {}, Error: {}",
                                serviceName, endpoint, ex.getMessage(), ex);
                        return Mono.just(createErrorResponse("Request failed: " + ex.getMessage()));
                    });

        } catch (Exception ex) {
            log.error("Microservice call failed: {} {}, Error: {}",
                    serviceName, endpoint, ex.getMessage(), ex);
            return Mono.just(createErrorResponse("Request failed: " + ex.getMessage()));
        }
    }

    /**
     * 转换参数名称（snake_case -> camelCase）
     */
    private Map<String, Object> convertParameters(
            Map<String, Object> parameters,
            Map<String, String> paramMapping) {

        if (paramMapping == null || paramMapping.isEmpty()) {
            return parameters;
        }

        Map<String, Object> converted = new HashMap<>();
        for (Map.Entry<String, Object> entry : parameters.entrySet()) {
            String key = entry.getKey();
            String convertedKey = paramMapping.getOrDefault(key, key);
            converted.put(convertedKey, entry.getValue());
        }

        return converted;
    }

    /**
     * 创建成功响应
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
