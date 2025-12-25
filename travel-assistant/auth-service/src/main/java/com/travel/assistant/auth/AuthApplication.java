package com.travel.assistant.auth;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

/**
 * Auth Service 启动类
 */
@SpringBootApplication(scanBasePackages = {"com.travel.assistant.common", "com.travel.assistant.auth"})
@MapperScan("com.travel.assistant.auth.mapper")
@EnableDiscoveryClient
public class AuthApplication {

    public static void main(String[] args) {
        SpringApplication.run(AuthApplication.class, args);
    }
}
