package com.travel.assistant.common.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * 健康检查接口
 */
@RestController
@RequestMapping("/health")
@RequiredArgsConstructor
public class HealthController {

    @Value("${spring.application.name:unknown}")
    private String applicationName;

    @Value("${server.port:8080}")
    private String serverPort;

    /**
     * 基础健康检查
     */
    @GetMapping
    public Map<String, Object> health() {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "UP");
        result.put("application", applicationName);
        result.put("port", serverPort);
        result.put("timestamp", LocalDateTime.now().toString());
        return result;
    }

    /**
     * 详细信息健康检查
     */
    @GetMapping("/details")
    public Map<String, Object> details() {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "UP");
        result.put("application", applicationName);
        result.put("port", serverPort);
        result.put("javaVersion", System.getProperty("java.version"));
        result.put("timestamp", LocalDateTime.now().toString());
        return result;
    }
}
