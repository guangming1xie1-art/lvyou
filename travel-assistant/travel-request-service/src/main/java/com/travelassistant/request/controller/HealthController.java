package com.travelassistant.request.controller;

import com.travelassistant.common.api.ApiResponse;
import com.travelassistant.common.dto.HealthStatus;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@Tag(name = "Health / 健康检查", description = "Service health endpoints / 服务健康检查接口")
public class HealthController {

  @GetMapping("/health")
  @Operation(summary = "Health check / 健康检查", description = "Returns service health status / 返回服务健康状态")
  @ApiResponses({
      @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "OK")
  })
  public ApiResponse<HealthStatus> health() {
    return ApiResponse.success(new HealthStatus("UP"));
  }
}
