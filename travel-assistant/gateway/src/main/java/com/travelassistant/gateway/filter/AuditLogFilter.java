package com.travelassistant.gateway.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.net.InetSocketAddress;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Component
@Slf4j
public class AuditLogFilter implements GlobalFilter, Ordered {

    private static final DateTimeFormatter DATE_TIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS");

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        long startTime = System.currentTimeMillis();
        ServerHttpRequest request = exchange.getRequest();
        
        String userId = request.getHeaders().getFirst("X-User-ID");
        String path = request.getURI().getPath();
        String method = request.getMethod() != null ? request.getMethod().name() : "UNKNOWN";
        String clientIp = getClientIp(request);
        String userAgent = request.getHeaders().getFirst("User-Agent");
        
        log.info("开始API调用 - 用户ID: {}, 方法: {} {}, IP: {}, User-Agent: {}, 时间: {}", 
            userId, method, path, clientIp, userAgent, LocalDateTime.now().format(DATE_TIME_FORMATTER));
        
        return chain.filter(exchange)
            .doFinally(signal -> {
                long duration = System.currentTimeMillis() - startTime;
                HttpStatus status = exchange.getResponse().getStatusCode();
                
                log.info("完成API调用 - 用户ID: {}, 方法: {} {}, 状态: {}, 耗时: {}ms, IP: {}, 时间: {}", 
                    userId, method, path, status, duration, clientIp, LocalDateTime.now().format(DATE_TIME_FORMATTER));
            });
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
        return -98;  // 最后执行
    }
}
