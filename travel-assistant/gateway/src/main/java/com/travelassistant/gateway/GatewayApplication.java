package com.travelassistant.gateway;

import com.travelassistant.gateway.mcp.tools.TravelMcpTools;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.context.annotation.Bean;

@SpringBootApplication(exclude = {
        DataSourceAutoConfiguration.class,
        HibernateJpaAutoConfiguration.class
})
//@SpringBootApplication
@EnableDiscoveryClient
@Slf4j
public class GatewayApplication {
  public static void main(String[] args) {
    SpringApplication.run(GatewayApplication.class, args);
    log.info("Gateway started successfully");
  }
  // 关键：注册工具提供器
  @Bean
  public ToolCallbackProvider travelTools(TravelMcpTools travelMcpTools) {
    return MethodToolCallbackProvider.builder()
            .toolObjects(travelMcpTools)
            .build();
  }
}
