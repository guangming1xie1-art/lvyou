package com.travelassistant.common.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Echo response payload / 回显响应数据")
public record EchoResponse(
    @Schema(description = "Echo content / 回显内容", example = "hello") String q
) {
}
