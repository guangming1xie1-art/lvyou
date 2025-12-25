package com.travel.assistant.order;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

/**
 * Order Service 启动类
 */
@SpringBootApplication(scanBasePackages = {"com.travel.assistant.common", "com.travel.assistant.order"})
@MapperScan("com.travel.assistant.order.mapper")
@EnableDiscoveryClient
public class OrderApplication {

    public static void main(String[] args) {
        SpringApplication.run(OrderApplication.class, args);
    }
}
