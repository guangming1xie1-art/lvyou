package com.travelassistant.common.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Health check response / 健康检查响应")
public record HealthStatus(
    @Schema(description = "Service status / 服务状态", example = "UP") String status
) {
}
