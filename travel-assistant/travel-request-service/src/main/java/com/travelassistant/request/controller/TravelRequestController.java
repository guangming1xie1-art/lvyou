package com.travelassistant.request.controller;

import com.travelassistant.common.api.ApiResponse;
import jakarta.validation.constraints.NotBlank;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/requests")
@Validated
public class TravelRequestController {

  @GetMapping("/echo")
  public ApiResponse<Map<String, String>> echo(@RequestParam @NotBlank String q) {
    return ApiResponse.success(Map.of("q", q));
  }
}
