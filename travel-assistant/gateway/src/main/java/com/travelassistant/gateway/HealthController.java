package com.travelassistant.gateway;

import com.travelassistant.common.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/health")
public class HealthController {
  
  @GetMapping
  public ApiResponse<Map<String, String>> health() {
    return ApiResponse.success(Map.of("status", "UP"));
  }

  @GetMapping("/ready")
  public ApiResponse<Map<String, String>> ready() {
    return ApiResponse.success(Map.of("status", "READY"));
  }
}
