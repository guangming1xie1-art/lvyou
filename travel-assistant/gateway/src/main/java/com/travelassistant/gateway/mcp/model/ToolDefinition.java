package com.travelassistant.gateway.mcp.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * MCP 工具定义模型
 * 用于描述一个可以被 MCP 客户端调用的工具
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ToolDefinition {
    /**
     * 工具唯一标识（如 "search_hotels"）
     */
    private String id;

    /**
     * 工具名称
     */
    private String name;

    /**
     * 工具描述
     */
    private String description;

    /**
     * JSON Schema 格式的输入参数定义
     */
    private Map<String, Object> inputSchema;

    /**
     * 目标微服务名称（如 "hotel-service"）
     */
    private String serviceName;

    /**
     * HTTP 方法（GET, POST, PUT, DELETE）
     */
    private String httpMethod;

    /**
     * API 端点路径（如 "/api/hotel/search"）
     */
    private String endpoint;

    /**
     * 参数名映射（snake_case 到 camelCase）
     * key: MCP 参数名（snake_case）
     * value: Java 服务参数名（camelCase）
     */
    private Map<String, String> paramMapping;
}
