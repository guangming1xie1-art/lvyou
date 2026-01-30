package com.travelassistant.gateway.mcp;

import com.travelassistant.gateway.mcp.model.ToolDefinition;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;

import java.util.HashMap;
import java.util.Map;

/**
 * MCP 工具路由器
 * 负责将 MCP 工具调用路由到对应的微服务
 */
@Slf4j
@Component
public class MCPToolRouter {

    private final MCPToolRegistry toolRegistry;
    private final WebClient webClient;

    @Autowired
    public MCPToolRouter(MCPToolRegistry toolRegistry, WebClient.Builder webClientBuilder) {
        this.toolRegistry = toolRegistry;
        this.webClient = webClientBuilder
                .baseUrl("lb://")
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(10 * 1024 * 1024))
                .build();
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

        // 1. 获取工具定义
        ToolDefinition tool = toolRegistry.getTool(toolName);
        if (tool == null) {
            log.warn("Tool not found: {}", toolName);
            return Mono.just(createErrorResponse("Tool not found: " + toolName));
        }

        log.info("Routing tool call: {} -> {}{}",
                toolName, tool.getServiceName(), tool.getEndpoint());

        // 2. 构建服务 URL
        String serviceUrl = tool.getServiceName();
        String endpoint = tool.getEndpoint();

        // 3. 转换参数名称（snake_case -> camelCase）
        Map<String, Object> convertedParams = convertParameters(parameters, tool.getParamMapping());

        // 4. 根据工具类型构建请求
        try {
            String httpMethod = tool.getHttpMethod().toUpperCase();

            switch (httpMethod) {
                case "GET":
                    return handleGetRequest(serviceUrl, endpoint, convertedParams, authHeader, toolName, tool.getParamMapping());
                case "POST":
                    return handlePostRequest(serviceUrl, endpoint, convertedParams, authHeader, toolName);
                case "PUT":
                    return handlePutRequest(serviceUrl, endpoint, convertedParams, authHeader, toolName);
                case "DELETE":
                    return handleDeleteRequest(serviceUrl, endpoint, convertedParams, authHeader, toolName);
                default:
                    log.error("Unsupported HTTP method: {}", httpMethod);
                    return Mono.just(createErrorResponse("Unsupported HTTP method: " + httpMethod));
            }
        } catch (Exception e) {
            log.error("Error routing tool call {}: {}", toolName, e.getMessage(), e);
            return Mono.just(createErrorResponse("Routing error: " + e.getMessage()));
        }
    }

    /**
     * 处理 GET 请求
     */
    private Mono<Map<String, Object>> handleGetRequest(
            String serviceUrl,
            String endpoint,
            Map<String, Object> parameters,
            String authHeader,
            String toolName,
            Map<String, String> paramMapping) {

        // 处理路径参数（如 /api/hotel/{id}）
        String processedEndpoint = endpoint;
        Map<String, Object> queryParams = new HashMap<>(parameters);

        // 检查是否有路径参数
        if (processedEndpoint.contains("{")) {
            // 先转换参数名称（snake_case -> camelCase）
            Map<String, Object> convertedParams = convertParameters(parameters, paramMapping);

            // 查找路径参数（原始名称和转换后的名称都要检查）
            Map<String, String> pathParamMap = new HashMap<>();
            for (Map.Entry<String, String> entry : paramMapping.entrySet()) {
                pathParamMap.put(entry.getValue(), entry.getKey()); // camelCase -> snake_case
            }

            for (Map.Entry<String, Object> entry : parameters.entrySet()) {
                // 检查原始名称
                String placeholder = "{" + entry.getKey() + "}";
                if (processedEndpoint.contains(placeholder)) {
                    processedEndpoint = processedEndpoint.replace(placeholder, String.valueOf(entry.getValue()));
                    queryParams.remove(entry.getKey());
                    continue;
                }

                // 检查转换后的名称
                String convertedKey = paramMapping.get(entry.getKey());
                if (convertedKey != null) {
                    placeholder = "{" + convertedKey + "}";
                    if (processedEndpoint.contains(placeholder)) {
                        processedEndpoint = processedEndpoint.replace(placeholder, String.valueOf(entry.getValue()));
                        queryParams.remove(entry.getKey());
                    }
                }
            }
        }
        // 增加这行：赋值给 final 变量
        final String finalEndpoint = processedEndpoint;
        // 构建请求
        WebClient.RequestHeadersSpec<?> request = webClient
                .get()
                .uri(uriBuilder -> {
                    uriBuilder.path(serviceUrl + finalEndpoint);
                    queryParams.forEach(uriBuilder::queryParam);
                    return uriBuilder.build();
                })
                .accept(MediaType.APPLICATION_JSON);

        // 添加 Authorization header
        if (authHeader != null && !authHeader.isEmpty()) {
            request.header(HttpHeaders.AUTHORIZATION, authHeader);
        }

        return request
                .retrieve()
                .bodyToMono(Object.class)
                .map(response -> createSuccessResponse(response))
                .onErrorResume(WebClientResponseException.class, ex -> {
                    log.error("GET request failed for {}: Status {}, Body: {}",
                            toolName, ex.getStatusCode(), ex.getResponseBodyAsString());
                    return Mono.just(createErrorResponse(
                            "Service error: " + ex.getStatusCode() + " - " + ex.getMessage()));
                })
                .onErrorResume(Exception.class, ex -> {
                    log.error("GET request failed for {}: {}", toolName, ex.getMessage(), ex);
                    return Mono.just(createErrorResponse("Request failed: " + ex.getMessage()));
                });
    }

    /**
     * 处理 POST 请求
     */
    private Mono<Map<String, Object>> handlePostRequest(
            String serviceUrl,
            String endpoint,
            Map<String, Object> parameters,
            String authHeader,
            String toolName) {

        // 处理路径参数
        String processedEndpoint = endpoint;
        Map<String, Object> bodyParams = new HashMap<>(parameters);

        // 检查是否有路径参数
        if (processedEndpoint.contains("{")) {
            for (Map.Entry<String, Object> entry : parameters.entrySet()) {
                String placeholder = "{" + entry.getKey() + "}";
                if (processedEndpoint.contains(placeholder)) {
                    processedEndpoint = processedEndpoint.replace(placeholder, String.valueOf(entry.getValue()));
                    bodyParams.remove(entry.getKey());
                }
            }
        }

        // 构建请求
        WebClient.RequestBodySpec request = webClient
                .post()
                .uri(serviceUrl + processedEndpoint)
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.APPLICATION_JSON);

        // 添加 Authorization header
        if (authHeader != null && !authHeader.isEmpty()) {
            request.header(HttpHeaders.AUTHORIZATION, authHeader);
        }

        return request
                .body(BodyInserters.fromValue(bodyParams))
                .retrieve()
                .bodyToMono(Object.class)
                .map(response -> createSuccessResponse(response))
                .onErrorResume(WebClientResponseException.class, ex -> {
                    log.error("POST request failed for {}: Status {}, Body: {}",
                            toolName, ex.getStatusCode(), ex.getResponseBodyAsString());
                    return Mono.just(createErrorResponse(
                            "Service error: " + ex.getStatusCode() + " - " + ex.getMessage()));
                })
                .onErrorResume(Exception.class, ex -> {
                    log.error("POST request failed for {}: {}", toolName, ex.getMessage(), ex);
                    return Mono.just(createErrorResponse("Request failed: " + ex.getMessage()));
                });
    }

    /**
     * 处理 PUT 请求
     */
    private Mono<Map<String, Object>> handlePutRequest(
            String serviceUrl,
            String endpoint,
            Map<String, Object> parameters,
            String authHeader,
            String toolName) {

        // 处理路径参数
        String processedEndpoint = endpoint;
        Map<String, Object> bodyParams = new HashMap<>(parameters);

        // 检查是否有路径参数
        if (processedEndpoint.contains("{")) {
            for (Map.Entry<String, Object> entry : parameters.entrySet()) {
                String placeholder = "{" + entry.getKey() + "}";
                if (processedEndpoint.contains(placeholder)) {
                    processedEndpoint = processedEndpoint.replace(placeholder, String.valueOf(entry.getValue()));
                    bodyParams.remove(entry.getKey());
                }
            }
        }

        // 构建请求
        WebClient.RequestBodySpec request = webClient
                .put()
                .uri(serviceUrl + processedEndpoint)
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.APPLICATION_JSON);

        // 添加 Authorization header
        if (authHeader != null && !authHeader.isEmpty()) {
            request.header(HttpHeaders.AUTHORIZATION, authHeader);
        }

        return request
                .body(BodyInserters.fromValue(bodyParams))
                .retrieve()
                .bodyToMono(Object.class)
                .map(response -> createSuccessResponse(response))
                .onErrorResume(WebClientResponseException.class, ex -> {
                    log.error("PUT request failed for {}: Status {}, Body: {}",
                            toolName, ex.getStatusCode(), ex.getResponseBodyAsString());
                    return Mono.just(createErrorResponse(
                            "Service error: " + ex.getStatusCode() + " - " + ex.getMessage()));
                })
                .onErrorResume(Exception.class, ex -> {
                    log.error("PUT request failed for {}: {}", toolName, ex.getMessage(), ex);
                    return Mono.just(createErrorResponse("Request failed: " + ex.getMessage()));
                });
    }

    /**
     * 处理 DELETE 请求
     */
    private Mono<Map<String, Object>> handleDeleteRequest(
            String serviceUrl,
            String endpoint,
            Map<String, Object> parameters,
            String authHeader,
            String toolName) {

        // 处理路径参数
        String processedEndpoint = endpoint;

        // 检查是否有路径参数
        if (processedEndpoint.contains("{")) {
            for (Map.Entry<String, Object> entry : parameters.entrySet()) {
                String placeholder = "{" + entry.getKey() + "}";
                if (processedEndpoint.contains(placeholder)) {
                    processedEndpoint = processedEndpoint.replace(placeholder, String.valueOf(entry.getValue()));
                }
            }
        }

        // 构建请求
        WebClient.RequestHeadersSpec<?> request = webClient
                .delete()
                .uri(serviceUrl + processedEndpoint)
                .accept(MediaType.APPLICATION_JSON);

        // 添加 Authorization header
        if (authHeader != null && !authHeader.isEmpty()) {
            request.header(HttpHeaders.AUTHORIZATION, authHeader);
        }

        return request
                .retrieve()
                .bodyToMono(Object.class)
                .map(response -> createSuccessResponse(response))
                .onErrorResume(WebClientResponseException.class, ex -> {
                    log.error("DELETE request failed for {}: Status {}, Body: {}",
                            toolName, ex.getStatusCode(), ex.getResponseBodyAsString());
                    return Mono.just(createErrorResponse(
                            "Service error: " + ex.getStatusCode() + " - " + ex.getMessage()));
                })
                .onErrorResume(Exception.class, ex -> {
                    log.error("DELETE request failed for {}: {}", toolName, ex.getMessage(), ex);
                    return Mono.just(createErrorResponse("Request failed: " + ex.getMessage()));
                });
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
            // 如果有映射，使用映射后的名称；否则使用原始名称
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
