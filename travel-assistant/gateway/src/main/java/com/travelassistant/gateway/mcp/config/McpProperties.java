package com.travelassistant.gateway.mcp.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

@Data
@Component
@ConfigurationProperties(prefix = "mcp")
public class McpProperties {

    private Map<String, ToolConfig> tools = new HashMap<>();

    @Data
    public static class ToolConfig {
        private String name;
        private String description;
        private String service;
        private String path;
        private String method = "GET";
        private boolean enabled = true;
    }
}
