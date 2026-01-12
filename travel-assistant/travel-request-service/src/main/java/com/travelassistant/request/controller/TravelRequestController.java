package com.travelassistant.request.controller;

import com.travelassistant.common.api.ApiResponse;
import com.travelassistant.common.dto.EchoResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.constraints.NotBlank;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/requests")
@Validated
@Tag(name = "Travel Requests / 旅行请求", description = "Travel request related APIs / 旅行请求相关接口")
public class TravelRequestController {

  @GetMapping("/echo")
  @Operation(summary = "Echo / 回显", description = "Echoes back the provided query string / 回显传入的查询字符串")
  @ApiResponses({
      @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "OK"),
      @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Bad Request / 参数错误"),
      @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Internal Server Error / 服务器内部错误")
  })
  public ApiResponse<EchoResponse> echo(
      @Parameter(description = "Query / 查询内容", required = true, example = "hello")
      @RequestParam @NotBlank String q
  ) {
    return ApiResponse.success(new EchoResponse(q));
  }
}
