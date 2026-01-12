package com.travelassistant.plan.controller;

import com.travelassistant.common.api.ApiResponse;
import com.travelassistant.common.dto.MessageResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/plans")
@Tag(name = "Travel Plans / 旅行规划", description = "Travel plan related APIs / 旅行规划相关接口")
public class TravelPlanController {

  @GetMapping("/sample")
  @Operation(summary = "Sample endpoint / 示例接口", description = "Simple readiness endpoint for travel-plan-service / travel-plan-service 就绪示例")
  @ApiResponses({
      @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "OK")
  })
  public ApiResponse<MessageResponse> sample() {
    return ApiResponse.success(new MessageResponse("travel-plan-service is ready"));
  }
}
