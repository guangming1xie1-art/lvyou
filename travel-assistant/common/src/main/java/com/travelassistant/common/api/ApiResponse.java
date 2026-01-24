package com.travelassistant.common.api;

import com.fasterxml.jackson.annotation.JsonInclude;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.Instant;

@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(description = "Unified API response wrapper / 统一 API 响应包装")
public class ApiResponse<T> {
  @Schema(description = "Business status code / 业务状态码", example = "0")
  private final int code;

  @Schema(description = "Message / 提示信息", example = "OK")
  private final String message;

  @Schema(description = "Response payload / 返回数据")
  private final T data;

  @Schema(description = "Response timestamp (UTC) / 响应时间戳 (UTC)")
  private final Instant timestamp;

  private ApiResponse(int code, String message, T data) {
    this.code = code;
    this.message = message;
    this.data = data;
    this.timestamp = Instant.now();
  }

  public static <T> ApiResponse<T> success(T data) {
    return new ApiResponse<>(ResultCode.SUCCESS.getCode(), ResultCode.SUCCESS.getMessage(), data);
  }

  public static ApiResponse<Void> success() {
    return success(null);
  }

  public static ApiResponse<Void> error(ResultCode resultCode) {
    return new ApiResponse<>(resultCode.getCode(), resultCode.getMessage(), null);
  }

  public static <T> ApiResponse<T> error(int code, String message) {
    return new ApiResponse<>(code, message, null);
  }
  public static <T> ApiResponse<T> error(String message) {
    return new ApiResponse<>(ResultCode.INTERNAL_ERROR.getCode(), message, null);
  }
  public int getCode() {
    return code;
  }

  public String getMessage() {
    return message;
  }

  public T getData() {
    return data;
  }

  public Instant getTimestamp() {
    return timestamp;
  }
}
