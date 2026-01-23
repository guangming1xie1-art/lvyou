package com.travelassistant.gateway.filter;

import com.travelassistant.common.util.JwtUtil;
import io.jsonwebtoken.Claims;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.core.io.buffer.DataBufferFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;

@Component
@Slf4j
public class JwtAuthenticationFilter implements GlobalFilter, Ordered {

    private static final List<String> PUBLIC_ROUTES = Arrays.asList(
            "/api/auth/login",
            "/api/auth/register", 
            "/api/auth/refresh",
            "/health",
            "/health/ready",
            "/actuator/health"
    );

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getURI().getPath();
        
        // 跳过公开路由
        if (isPublicRoute(path)) {
            log.debug("跳过公开路由: {}", path);
            return chain.filter(exchange);
        }
        
        try {
            // 从Authorization header获取token
            String token = getTokenFromRequest(request);
            if (token == null) {
                log.warn("缺少认证token: {}", path);
                return onError(exchange, "Missing authorization token", HttpStatus.UNAUTHORIZED);
            }
            
            // 验证token并提取用户信息
            Claims claims = JwtUtil.verifyToken(token);
            String userId = claims.getSubject();
            String username = (String) claims.get("username");
            
            // 检查token是否过期
            if (JwtUtil.isTokenExpired(claims)) {
                log.warn("Token已过期 - 用户ID: {}, 路径: {}", userId, path);
                return onError(exchange, "Token expired", HttpStatus.UNAUTHORIZED);
            }
            
            // 创建新的request，添加用户上下文header
            ServerHttpRequest newRequest = request.mutate()
                .header("X-User-ID", userId != null ? userId : "unknown")
                .header("X-Username", username != null ? username : "unknown")
                .header("X-Auth-Token", token)
                .build();
            
            log.info("JWT验证成功 - 用户ID: {}, 用户名: {}, 路径: {}", userId, username, path);
            
            // 继续filter chain，传递修改后的request
            return chain.filter(exchange.mutate().request(newRequest).build());
            
        } catch (Exception e) {
            log.warn("JWT验证失败: {}, 路径: {}", e.getMessage(), path);
            return onError(exchange, "Invalid token: " + e.getMessage(), HttpStatus.UNAUTHORIZED);
        }
    }
    
    private boolean isPublicRoute(String path) {
        return PUBLIC_ROUTES.stream().anyMatch(path::startsWith);
    }
    
    private String getTokenFromRequest(ServerHttpRequest request) {
        String authHeader = request.getHeaders().getFirst("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            return authHeader.substring(7);
        }
        return null;
    }
    
    private Mono<Void> onError(ServerWebExchange exchange, String message, HttpStatus status) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(status);
        response.getHeaders().setContentType(MediaType.APPLICATION_JSON);
        
        String errorBody = String.format("{\"error\": \"%s\", \"status\": %d}", message, status.value());
        DataBuffer dataBuffer = response.bufferFactory().wrap(errorBody.getBytes(StandardCharsets.UTF_8));
        return response.writeWith(Mono.just(dataBuffer));
    }
    
    @Override
    public int getOrder() {
        return -100;  // 最高优先级
    }
}
