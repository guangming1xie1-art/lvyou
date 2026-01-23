package com.travelassistant.gateway.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

@Component
@Slf4j
public class RateLimitFilter implements GlobalFilter, Ordered {

    private static final int RATE_LIMIT_PER_MINUTE = 100;
    private static final Duration RATE_LIMIT_WINDOW = Duration.ofMinutes(1);
    
    private final RedisTemplate<String, Integer> redisTemplate;

    public RateLimitFilter(RedisTemplate<String, Integer> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        
        // 从header获取用户ID，如果没有则使用IP地址
        String userId = request.getHeaders().getFirst("X-User-ID");
        if (userId == null) {
            userId = getClientIp(request);
        }
        
        String rateLimitKey = "rate_limit:" + userId;
        ValueOperations<String, Integer> ops = redisTemplate.opsForValue();
        Integer currentCount = ops.get(rateLimitKey);
        
        if (currentCount == null) {
            currentCount = 0;
            ops.set(rateLimitKey, 0);
            redisTemplate.expire(rateLimitKey, RATE_LIMIT_WINDOW);
        }
        
        if (currentCount >= RATE_LIMIT_PER_MINUTE) {
            log.warn("速率限制触发 - 用户ID: {}, 当前计数: {}", userId, currentCount);
            ServerHttpResponse response = exchange.getResponse();
            response.setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
            response.getHeaders().setContentType(MediaType.APPLICATION_JSON);
            String errorBody = String.format("{\"error\": \"Too many requests\", \"status\": %d, \"limit\": %d}", 
                HttpStatus.TOO_MANY_REQUESTS.value(), RATE_LIMIT_PER_MINUTE);
            DataBuffer dataBuffer = response.bufferFactory().wrap(errorBody.getBytes(StandardCharsets.UTF_8));
            return response.writeWith(Mono.just(dataBuffer));
        }
        
        // 递增计数
        ops.increment(rateLimitKey);
        
        return chain.filter(exchange);
    }
    
    private String getClientIp(ServerHttpRequest request) {
        String clientIp = request.getHeaders().getFirst("X-Forwarded-For");
        if (clientIp == null || clientIp.isEmpty() || "unknown".equalsIgnoreCase(clientIp)) {
            InetSocketAddress address = request.getRemoteAddress();
            clientIp = address != null ? address.getHostString() : "unknown";
        }
        // 取第一个IP（如果有多级代理）
        if (clientIp.contains(",")) {
            clientIp = clientIp.split(",")[0].trim();
        }
        return clientIp;
    }
    
    @Override
    public int getOrder() {
        return -99;  // 在JwtAuthenticationFilter之后执行
    }
}
