package com.travel.assistant.gateway.filter;

import com.travel.assistant.common.utils.JwtUtils;
import com.travel.assistant.common.utils.LoginUser;
import com.travel.assistant.common.utils.SecurityContextHolder;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.Arrays;
import java.util.List;

/**
 * JWT 认证网关过滤器
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class AuthGatewayFilter implements GlobalFilter, Ordered {

    private final JwtUtils jwtUtils;

    /**
     * 无需认证的路径
     */
    private static final List<String> WHITE_LIST = Arrays.asList(
            "/auth/login",
            "/auth/register",
            "/health",
            "/swagger-ui",
            "/v3/api-docs",
            "/doc.html"
    );

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getPath().value();

        // 白名单路径直接放行
        if (isWhiteListed(path)) {
            return chain.filter(exchange);
        }

        // 获取 Token
        String authHeader = request.getHeaders().getFirst(jwtUtils.getHeader());
        String token = jwtUtils.getTokenFromHeader(authHeader);

        if (token == null) {
            log.warn("路径 {} 请求缺少认证信息", path);
            return unauthorizedResponse(exchange, "未登录或登录已过期");
        }

        // 验证 Token
        if (!jwtUtils.validateToken(token)) {
            log.warn("路径 {} 请求Token无效", path);
            return unauthorizedResponse(exchange, "Token无效");
        }

        // 检查 Token 是否过期
        if (jwtUtils.isTokenExpired(token)) {
            log.warn("路径 {} 请求Token已过期", path);
            return unauthorizedResponse(exchange, "Token已过期");
        }

        // 设置用户信息到请求头
        Long userId = jwtUtils.getUserId(token);
        String username = jwtUtils.getUsername(token);

        ServerHttpRequest mutatedRequest = request.mutate()
                .header("X-User-Id", String.valueOf(userId))
                .header("X-Username", username)
                .build();

        // 设置登录用户到上下文
        LoginUser loginUser = LoginUser.of(userId, username, "USER");
        SecurityContextHolder.setCurrentUser(loginUser);

        return chain.filter(exchange.mutate().request(mutatedRequest).build());
    }

    private boolean isWhiteListed(String path) {
        return WHITE_LIST.stream().anyMatch(path::contains);
    }

    private Mono<Void> unauthorizedResponse(ServerWebExchange exchange, String message) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.UNAUTHORIZED);
        response.getHeaders().add("Content-Type", "application/json;charset=UTF-8");
        String body = String.format("{\"code\":401,\"message\":\"%s\"}", message);
        return response.writeWith(Mono.just(response.bufferFactory().wrap(body.getBytes())));
    }

    @Override
    public int getOrder() {
        return -100;
    }
}
