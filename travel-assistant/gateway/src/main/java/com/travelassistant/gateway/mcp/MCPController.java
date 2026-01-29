package com.travelassistant.gateway.mcp;

import com.travelassistant.gateway.mcp.model.MCPResponse;
import com.travelassistant.gateway.mcp.model.ToolDefinition;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * MCP REST 控制器
 * 提供 MCP 协议的 HTTP 端点
 *
 * 遵循 MCP 协议规范（JSON-RPC 2.0）
 * 与 langchain_mcp_adapters 的 MultiServerMCPClient 完全兼容
 */
@Slf4j
@RestController
@RequestMapping("/mcp")
@Tag(name = "MCP Service", description = "Model Context Protocol 服务端点")
public class MCPController {

    private final MCPToolRegistry toolRegistry;
    private final MCPToolRouter toolRouter;
    private final MicroserviceToolAdapter microserviceToolAdapter;

    @Autowired
    public MCPController(
            MCPToolRegistry toolRegistry,
            MCPToolRouter toolRouter,
            MicroserviceToolAdapter microserviceToolAdapter) {
        this.toolRegistry = toolRegistry;
        this.toolRouter = toolRouter;
        this.microserviceToolAdapter = microserviceToolAdapter;

        log.info("MCP Server initialized with {} tools", toolRegistry.getAllTools().size());
    }

    /**
     * 获取所有工具定义
     */
    @GetMapping("/tools")
    @Operation(summary = "获取所有工具", description = "返回所有可用的 MCP 工具定义列表")
    public Mono<ResponseEntity<MCPResponse<List<ToolDefinition>>>> getAllTools() {
        try {
            List<ToolDefinition> tools = toolRegistry.getAllTools();
            log.info("Returning {} tools", tools.size());
            return Mono.just(ResponseEntity.ok(MCPResponse.success(tools)));
        } catch (Exception e) {
            log.error("Error getting all tools", e);
            return Mono.just(ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(MCPResponse.error("Failed to get tools: " + e.getMessage())));
        }
    }

    /**
     * 获取单个工具定义
     */
    @GetMapping("/tools/{toolName}")
    @Operation(summary = "获取工具详情", description = "根据工具名获取工具定义详情")
    public Mono<ResponseEntity<MCPResponse<ToolDefinition>>> getTool(
            @Parameter(description = "工具名称", required = true)
            @PathVariable String toolName) {
        try {
            ToolDefinition tool = toolRegistry.getTool(toolName);
            if (tool == null) {
                log.warn("Tool not found: {}", toolName);
                return Mono.just(ResponseEntity
                        .status(HttpStatus.NOT_FOUND)
                        .body(MCPResponse.error("Tool not found: " + toolName)));
            }

            log.info("Returning tool: {}", toolName);
            return Mono.just(ResponseEntity.ok(MCPResponse.success(tool)));
        } catch (Exception e) {
            log.error("Error getting tool: {}", toolName, e);
            return Mono.just(ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(MCPResponse.error("Failed to get tool: " + e.getMessage())));
        }
    }

    /**
     * 调用工具
     */
    @PostMapping("/tools/{toolName}/call")
    @Operation(summary = "调用工具", description = "执行指定的 MCP 工具并返回结果")
    public Mono<ResponseEntity<Map<String, Object>>> callTool(
            @Parameter(description = "工具名称", required = true)
            @PathVariable String toolName,
            @RequestBody Map<String, Object> requestBody,
            ServerWebExchange exchange) {

        // 提取参数
        @SuppressWarnings("unchecked")
        Map<String, Object> parameters = (Map<String, Object>) requestBody.getOrDefault("parameters", new HashMap<>());

        // 获取 Authorization header
        String authHeader = exchange.getRequest().getHeaders().getFirst("Authorization");

        log.info("Calling tool: {} with parameters: {}", toolName, parameters);

        // 路由并调用工具
        return toolRouter.routeAndCall(toolName, parameters, authHeader)
                .map(result -> {
                    boolean success = (Boolean) result.getOrDefault("success", false);
                    if (success) {
                        return ResponseEntity.ok(result);
                    } else {
                        return ResponseEntity
                                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                                .body(result);
                    }
                })
                .onErrorResume(Exception e -> {
                    log.error("Error calling tool: {}", toolName, e);
                    Map<String, Object> errorResponse = new HashMap<>();
                    errorResponse.put("success", false);
                    errorResponse.put("error", "Internal error: " + e.getMessage());
                    return Mono.just(ResponseEntity
                            .status(HttpStatus.INTERNAL_SERVER_ERROR)
                            .body(errorResponse));
                });
    }

    /**
     * MCP initialize 端点（JSON-RPC 2.0 兼容）
     * 兼容 MultiServerMCPClient 和标准 MCP 协议
     */
    @PostMapping("/initialize")
    @Operation(summary = "MCP 初始化", description = "MCP 协议初始化端点，返回协议版本和能力")
    public Mono<ResponseEntity<Map<String, Object>>> initialize() {
        log.info("MCP initialize called");

        Map<String, Object> response = new HashMap<>();

        // 协议版本
        response.put("protocolVersion", "2024-11-05");

        // 服务器能力
        Map<String, Object> capabilities = new HashMap<>();

        Map<String, Object> tools = new HashMap<>();
        tools.put("listChanged", false);
        capabilities.put("tools", tools);

        Map<String, Object> resources = new HashMap<>();
        resources.put("subscribe", false);
        resources.put("listChanged", false);
        capabilities.put("resources", resources);

        response.put("capabilities", capabilities);

        // 服务器信息
        Map<String, Object> serverInfo = new HashMap<>();
        serverInfo.put("name", "Travel Assistant Gateway MCP Server");
        serverInfo.put("version", "1.0.0");
        response.put("serverInfo", serverInfo);

        return Mono.just(ResponseEntity.ok(response));
    }

    /**
     * MCP JSON-RPC 2.0 端点
     * 标准 MCP 协议入口点，支持 initialize、tools/list、tools/call 等方法
     */
    @PostMapping
    @Operation(summary = "MCP JSON-RPC 2.0", description = "标准 MCP 协议端点（JSON-RPC 2.0）")
    public Mono<ResponseEntity<Map<String, Object>>> mcpJsonRpc(
            @RequestBody Map<String, Object> request,
            ServerWebExchange exchange) {

        // 提取 Authorization header 用于转发
        String authHeader = exchange.getRequest().getHeaders().getFirst("Authorization");

        log.info("MCP JSON-RPC request: {}", request);

        // JSON-RPC 2.0 基本字段
        String jsonrpc = (String) request.get("jsonrpc");
        String method = (String) request.get("method");
        Object id = request.get("id");
        Map<String, Object> params = (Map<String, Object>) request.getOrDefault("params", new HashMap<>());

        // 验证 JSON-RPC 2.0
        if (!"2.0".equals(jsonrpc)) {
            return Mono.just(createJsonRpcError(id, -32600, "Invalid Request", "jsonrpc version must be 2.0"));
        }

        if (method == null || method.isEmpty()) {
            return Mono.just(createJsonRpcError(id, -32600, "Invalid Request", "method is required"));
        }

        // 路由到对应的处理方法
        try {
            switch (method) {
                case "initialize":
                    return handleInitialize(id, params);
                case "tools/list":
                    return handleToolsList(id);
                case "tools/call":
                    return handleToolsCall(id, params, authHeader);
                default:
                    return Mono.just(createJsonRpcError(id, -32601, "Method not found", "Unknown method: " + method));
            }
        } catch (Exception e) {
            log.error("Error processing MCP request: {}", e.getMessage(), e);
            return Mono.just(createJsonRpcError(id, -32603, "Internal error", e.getMessage()));
        }
    }

    /**
     * 处理 initialize 方法
     */
    private Mono<ResponseEntity<Map<String, Object>>> handleInitialize(Object id, Map<String, Object> params) {
        Map<String, Object> result = new HashMap<>();

        // 协议版本
        result.put("protocolVersion", "2024-11-05");

        // 服务器能力
        Map<String, Object> capabilities = new HashMap<>();

        Map<String, Object> tools = new HashMap<>();
        tools.put("listChanged", false);
        capabilities.put("tools", tools);

        result.put("capabilities", capabilities);

        // 服务器信息
        Map<String, Object> serverInfo = new HashMap<>();
        serverInfo.put("name", "Travel Assistant Gateway MCP Server");
        serverInfo.put("version", "1.0.0");
        result.put("serverInfo", serverInfo);

        return Mono.just(createJsonRpcSuccess(id, result));
    }

    /**
     * 处理 tools/list 方法
     */
    private Mono<ResponseEntity<Map<String, Object>>> handleToolsList(Object id) {
        try {
            List<ToolDefinition> tools = toolRegistry.getAllTools();

            Map<String, Object> result = new HashMap<>();
            result.put("tools", tools);

            return Mono.just(createJsonRpcSuccess(id, result));
        } catch (Exception e) {
            log.error("Error getting tools list: {}", e.getMessage(), e);
            return Mono.just(createJsonRpcError(id, -32603, "Internal error", e.getMessage()));
        }
    }

    /**
     * 处理 tools/call 方法
     */
    private Mono<ResponseEntity<Map<String, Object>>> handleToolsCall(Object id, Map<String, Object> params, String authHeader) {
        try {
            String name = (String) params.get("name");
            @SuppressWarnings("unchecked")
            Map<String, Object> arguments = (Map<String, Object>) params.getOrDefault("arguments", new HashMap<>());

            if (name == null || name.isEmpty()) {
                return Mono.just(createJsonRpcError(id, -32602, "Invalid params", "Tool name is required"));
            }

            log.info("MCP tools/call: name={}, arguments={}", name, arguments);

            // 调用工具，传递 authHeader 用于转发到后端微服务
            return toolRouter.routeAndCall(name, arguments, authHeader)
                    .map(result -> {
                        // MCP 期望的返回格式
                        Map<String, Object> callResult = new HashMap<>();

                        if (result != null && Boolean.TRUE.equals(result.get("success"))) {
                            Object data = result.get("data");
                            if (data instanceof Map) {
                                callResult.put("content", List.of(Map.of(
                                    "type", "text",
                                    "text", data.toString()
                                )));
                            } else {
                                callResult.put("content", List.of(Map.of(
                                    "type", "text",
                                    "text", result.toString()
                                )));
                            }
                        } else {
                            // 错误情况
                            String error = result != null ? (String) result.get("error") : "Unknown error";
                            callResult.put("isError", true);
                            callResult.put("content", List.of(Map.of(
                                "type", "text",
                                "text", error
                            )));
                        }

                        return createJsonRpcSuccess(id, callResult);
                    })
                    .onErrorResume(Exception e -> {
                        log.error("Error calling tool {}: {}", name, e.getMessage(), e);
                        return Mono.just(createJsonRpcError(id, -32603, "Internal error", e.getMessage()));
                    });

        } catch (Exception e) {
            log.error("Error processing tools/call: {}", e.getMessage(), e);
            return Mono.just(createJsonRpcError(id, -32603, "Internal error", e.getMessage()));
        }
    }

    /**
     * 创建 JSON-RPC 2.0 成功响应
     */
    private ResponseEntity<Map<String, Object>> createJsonRpcSuccess(Object id, Object result) {
        Map<String, Object> response = new HashMap<>();
        response.put("jsonrpc", "2.0");
        response.put("id", id);
        response.put("result", result);
        return ResponseEntity.ok(response);
    }

    /**
     * 创建 JSON-RPC 2.0 错误响应
     */
    private ResponseEntity<Map<String, Object>> createJsonRpcError(
            Object id, int code, String message, String data) {

        Map<String, Object> error = new HashMap<>();
        error.put("code", code);
        error.put("message", message);
        if (data != null) {
            error.put("data", data);
        }

        Map<String, Object> response = new HashMap<>();
        response.put("jsonrpc", "2.0");
        response.put("id", id);
        response.put("error", error);

        return ResponseEntity.ok(response);
    }

    /**
     * Health check for MCP service
     */
    @GetMapping("/health")
    @Operation(summary = "健康检查", description = "MCP 服务健康检查")
    public Mono<ResponseEntity<Map<String, Object>>> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "healthy");
        health.put("service", "mcp");
        health.put("toolsCount", toolRegistry.getAllTools().size());
        return Mono.just(ResponseEntity.ok(health));
    }
}
