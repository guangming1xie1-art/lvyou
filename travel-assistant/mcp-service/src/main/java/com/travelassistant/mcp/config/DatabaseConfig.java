package com.travelassistant.mcp.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableJpaRepositories(basePackages = "com.travelassistant.mcp.repository")
@EnableTransactionManagement
public class DatabaseConfig {
}
