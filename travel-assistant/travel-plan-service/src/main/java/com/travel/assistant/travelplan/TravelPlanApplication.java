package com.travel.assistant.travelplan;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

/**
 * Travel Plan Service 启动类
 */
@SpringBootApplication(scanBasePackages = {"com.travel.assistant.common", "com.travel.assistant.travelplan"})
@MapperScan("com.travel.assistant.travelplan.mapper")
@EnableDiscoveryClient
public class TravelPlanApplication {

    public static void main(String[] args) {
        SpringApplication.run(TravelPlanApplication.class, args);
    }
}
