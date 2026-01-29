package com.travelassistant.gateway.mcp.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * MCP 统一响应格式
 * 用于 MCP 端点的响应包装
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MCPResponse<T> {
    /**
     * 是否成功
     */
    private boolean success;

    /**
     * 响应数据
     */
    private T data;

    /**
     * 错误信息（失败时）
     */
    private String error;

    /**
     * 创建成功响应
     */
    public static <T> MCPResponse<T> success(T data) {
        return MCPResponse.<T>builder()
                .success(true)
                .data(data)
                .build();
    }

    /**
     * 创建失败响应
     */
    public static <T> MCPResponse<T> error(String error) {
        return MCPResponse.<T>builder()
                .success(false)
                .error(error)
                .build();
    }
}
