package com.travelassistant.gateway.mcp;

import org.springframework.context.annotation.Configuration;

/**
 * MCP Server Configuration
 * 配置标准 MCP 协议支持（JSON-RPC 2.0）
 * 
 * MCP 协议实现详情：
 * - MCPController 提供标准 JSON-RPC 2.0 端点
 * - MCPToolRegistry 管理所有可用工具
 * - MCPToolRouter 负责将工具调用路由到后端微服务
 * - MicroserviceToolAdapter 将微服务 API 封装为 MCP 工具
 * 
 * 与 langchain_mcp_adapters 的 MultiServerMCPClient 完全兼容
 */
@Configuration
public class MCPServerConfiguration {
    // MCP Server 的具体实现在 MCPController 中
    // 这里作为配置标记类，用于文档说明和未来扩展
}
