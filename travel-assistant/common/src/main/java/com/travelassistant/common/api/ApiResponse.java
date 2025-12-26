package com.travelassistant.common.api;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.time.Instant;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {
  private final int code;
  private final String message;
  private final T data;
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

  public static ApiResponse<Void> error(int code, String message) {
    return new ApiResponse<>(code, message, null);
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
