package com.travelassistant.memory;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Memory Service 主应用类
 * 
 * 记忆系统微服务，负责存储和管理四层记忆系统的数据
 */
@SpringBootApplication
@EnableScheduling
public class MemoryServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(MemoryServiceApplication.class, args);
    }
}
