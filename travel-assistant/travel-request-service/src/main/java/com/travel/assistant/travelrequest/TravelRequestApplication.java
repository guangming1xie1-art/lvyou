package com.travel.assistant.travelrequest;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

/**
 * Travel Request Service 启动类
 */
@SpringBootApplication(scanBasePackages = {"com.travel.assistant.common", "com.travel.assistant.travelrequest"})
@MapperScan("com.travel.assistant.travelrequest.mapper")
@EnableDiscoveryClient
public class TravelRequestApplication {

    public static void main(String[] args) {
        SpringApplication.run(TravelRequestApplication.class, args);
    }
}
