package com.travelassistant.common.api;

public enum ResultCode {
  SUCCESS(0, "OK"),
  BAD_REQUEST(4000, "Bad request"),
  UNAUTHORIZED(4010, "Unauthorized"),
  FORBIDDEN(4030, "Forbidden"),
  NOT_FOUND(4040, "Not found"),
  INTERNAL_ERROR(5000, "Internal server error");

  private final int code;
  private final String message;

  ResultCode(int code, String message) {
    this.code = code;
    this.message = message;
  }

  public int getCode() {
    return code;
  }

  public String getMessage() {
    return message;
  }
}
