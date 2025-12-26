package com.travelassistant.order.controller;

import com.travelassistant.common.api.ApiResponse;
import com.travelassistant.common.api.ResultCode;
import com.travelassistant.common.exception.BusinessException;
import jakarta.validation.ConstraintViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

  @ExceptionHandler(BusinessException.class)
  @ResponseStatus(HttpStatus.OK)
  public ApiResponse<Void> handleBusiness(BusinessException e) {
    return ApiResponse.error(e.getCode(), e.getMessage());
  }

  @ExceptionHandler({MethodArgumentNotValidException.class, ConstraintViolationException.class})
  @ResponseStatus(HttpStatus.BAD_REQUEST)
  public ApiResponse<Void> handleValidation(Exception e) {
    String message = e.getMessage();
    return ApiResponse.error(ResultCode.BAD_REQUEST.getCode(), message == null ? ResultCode.BAD_REQUEST.getMessage() : message);
  }

  @ExceptionHandler(Exception.class)
  @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
  public ApiResponse<Void> handleOther(Exception e) {
    String message = e.getMessage();
    return ApiResponse.error(ResultCode.INTERNAL_ERROR.getCode(), message == null ? ResultCode.INTERNAL_ERROR.getMessage() : message);
  }
}
