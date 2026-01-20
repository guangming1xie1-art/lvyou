package com.travelassistant.mcp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class McpServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(McpServiceApplication.class, args);
    }
}
