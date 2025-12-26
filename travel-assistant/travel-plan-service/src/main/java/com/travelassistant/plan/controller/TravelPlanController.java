package com.travelassistant.plan.controller;

import com.travelassistant.common.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/plans")
public class TravelPlanController {

  @GetMapping("/sample")
  public ApiResponse<Map<String, String>> sample() {
    return ApiResponse.success(Map.of("message", "travel-plan-service is ready"));
  }
}
