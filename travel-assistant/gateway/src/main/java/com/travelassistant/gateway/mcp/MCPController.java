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
 * MCP REST 控制器 (已废弃)
 * 
 * ⚠️ 重要说明：
 * 此控制器提供的是自定义 REST API 实现，用于向后兼容。
 * 
 * 新的标准 MCP Protocol 由 Spring AI MCP Server 自动处理，
 * 端点为 /mcp (由 spring-ai-mcp-server-spring-boot-starter 提供)
 * 
 * 推荐使用标准 MCP Protocol 端点：
 * - POST /mcp/initialize - MCP 协议初始化
 * - GET  /mcp/tools/list - 获取工具列表
 * - POST /mcp/tools/call - 调用工具
 * 
 * @deprecated 使用 Spring AI MCP Server 标准端点替代
 */
@Slf4j
@RestController
@RequestMapping("/mcp")
@Tag(name = "MCP Service (Legacy)", description = "Model Context Protocol 服务端点（已废弃，请使用标准 MCP 端点）")
@Deprecated(since = "2.0.0", forRemoval = false)
public class MCPController {

    private final MCPToolRegistry toolRegistry;
    private final MCPToolRouter toolRouter;

    @Autowired
    public MCPController(MCPToolRegistry toolRegistry, MCPToolRouter toolRouter) {
        this.toolRegistry = toolRegistry;
        this.toolRouter = toolRouter;
    }

    /**
     * 获取所有工具定义 (已废弃)
     * 
     * @deprecated 使用标准 MCP 端点 GET /mcp/tools/list
     */
    @Deprecated(since = "2.0.0")
    @GetMapping("/tools")
    @Operation(summary = "获取所有工具 (已废弃)", description = "返回所有可用的 MCP 工具定义列表。已废弃，请使用标准 MCP 端点 GET /mcp/tools/list")
    public Mono<ResponseEntity<MCPResponse<List<ToolDefinition>>>> getAllTools() {
        log.warn("Deprecated endpoint /mcp/tools called. Use standard MCP endpoint /mcp/tools/list instead.");
        try {
            List<ToolDefinition> tools = toolRegistry.getAllTools();
            log.info("Returning {} tools (legacy endpoint)", tools.size());
            return Mono.just(ResponseEntity.ok(MCPResponse.success(tools)));
        } catch (Exception e) {
            log.error("Error getting all tools", e);
            return Mono.just(ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(MCPResponse.error("Failed to get tools: " + e.getMessage())));
        }
    }

    /**
     * 获取单个工具定义 (已废弃)
     * 
     * @deprecated 使用标准 MCP 协议获取工具信息
     */
    @Deprecated(since = "2.0.0")
    @GetMapping("/tools/{toolName}")
    @Operation(summary = "获取工具详情 (已废弃)", description = "根据工具名获取工具定义详情。已废弃，请使用标准 MCP 端点")
    public Mono<ResponseEntity<MCPResponse<ToolDefinition>>> getTool(
            @Parameter(description = "工具名称", required = true)
            @PathVariable String toolName) {
        log.warn("Deprecated endpoint /mcp/tools/{} called. Use standard MCP endpoint instead.", toolName);
        try {
            ToolDefinition tool = toolRegistry.getTool(toolName);
            if (tool == null) {
                log.warn("Tool not found: {}", toolName);
                return Mono.just(ResponseEntity
                        .status(HttpStatus.NOT_FOUND)
                        .body(MCPResponse.error("Tool not found: " + toolName)));
            }

            log.info("Returning tool: {} (legacy endpoint)", toolName);
            return Mono.just(ResponseEntity.ok(MCPResponse.success(tool)));
        } catch (Exception e) {
            log.error("Error getting tool: {}", toolName, e);
            return Mono.just(ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(MCPResponse.error("Failed to get tool: " + e.getMessage())));
        }
    }

    /**
     * 调用工具 (已废弃)
     * 
     * @deprecated 使用标准 MCP 端点 POST /mcp/tools/call
     */
    @Deprecated(since = "2.0.0")
    @PostMapping("/tools/{toolName}/call")
    @Operation(summary = "调用工具 (已废弃)", description = "执行指定的 MCP 工具并返回结果。已废弃，请使用标准 MCP 端点 POST /mcp/tools/call")
    public Mono<ResponseEntity<Map<String, Object>>> callTool(
            @Parameter(description = "工具名称", required = true)
            @PathVariable String toolName,
            @RequestBody Map<String, Object> requestBody,
            ServerWebExchange exchange) {

        log.warn("Deprecated endpoint /mcp/tools/{}/call called. Use standard MCP endpoint /mcp/tools/call instead.", toolName);

        // 提取参数
        @SuppressWarnings("unchecked")
        Map<String, Object> parameters = (Map<String, Object>) requestBody.getOrDefault("parameters", new HashMap<>());

        // 获取 Authorization header
        String authHeader = exchange.getRequest().getHeaders().getFirst("Authorization");

        log.info("Calling tool: {} with parameters: {} (legacy endpoint)", toolName, parameters);

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
     * MCP initialize 端点 (已废弃)
     * 兼容 MultiServerMCPClient
     * 
     * @deprecated 使用标准 MCP 端点 POST /mcp/initialize
     */
    @Deprecated(since = "2.0.0")
    @PostMapping("/initialize")
    @Operation(summary = "MCP 初始化 (已废弃)", description = "MCP 协议初始化端点，返回协议版本和能力。已废弃，请使用标准 MCP 端点 POST /mcp/initialize")
    public Mono<ResponseEntity<Map<String, Object>>> initialize() {
        log.warn("Deprecated endpoint /mcp/initialize called. Use standard MCP endpoint instead.");

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
        serverInfo.put("name", "Travel Assistant Gateway MCP Server (Legacy)");
        serverInfo.put("version", "1.0.0-deprecated");
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
        health.put("mode", "spring-ai-mcp-server");
        health.put("legacyToolsCount", toolRegistry.getAllTools().size());
        health.put("note", "MCPController is deprecated. Spring AI MCP Server is now active.");
        return Mono.just(ResponseEntity.ok(health));
    }
}
