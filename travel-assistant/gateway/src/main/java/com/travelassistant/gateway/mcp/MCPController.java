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
 */
@Slf4j
@RestController
@RequestMapping("/mcp")
@Tag(name = "MCP Service", description = "Model Context Protocol 服务端点")
public class MCPController {

    private final MCPToolRegistry toolRegistry;
    private final MCPToolRouter toolRouter;

    @Autowired
    public MCPController(MCPToolRegistry toolRegistry, MCPToolRouter toolRouter) {
        this.toolRegistry = toolRegistry;
        this.toolRouter = toolRouter;
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
     * MCP initialize 端点
     * 兼容 MultiServerMCPClient
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
