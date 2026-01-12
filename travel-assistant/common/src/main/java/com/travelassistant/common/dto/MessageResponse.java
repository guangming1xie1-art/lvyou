package com.travelassistant.common.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Simple message response / 简单消息响应")
public record MessageResponse(
    @Schema(description = "Message / 消息", example = "service is ready") String message
) {
}
