package com.travel.assistant.gateway.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;

/**
 * Gateway 路由配置
 */
@Configuration
public class GatewayRouteConfig {

    @Bean
    public RouteLocator routes(RouteLocatorBuilder builder) {
        return builder.routes()
                // 认证服务
                .route("auth-service", r -> r.path("/api/auth/**")
                        .uri("lb://auth-service")
                        .filter(authGatewayFilter()))

                // 旅游请求服务
                .route("travel-request-service", r -> r.path("/api/travel-request/**")
                        .uri("lb://travel-request-service"))

                // 旅游计划服务
                .route("travel-plan-service", r -> r.path("/api/travel-plan/**")
                        .uri("lb://travel-plan-service"))

                // 订单服务
                .route("order-service", r -> r.path("/api/order/**")
                        .uri("lb://order-service"))

                // 公开接口（健康检查、Swagger等）
                .route("public", r -> r.path("/health/**", "/swagger-ui/**",
                                "/v3/api-docs/**", "/doc.html/**")
                        .uri("lb://gateway"))

                .build();
    }

    @Bean
    public AuthGatewayFilter authGatewayFilter() {
        return new AuthGatewayFilter();
    }
}
