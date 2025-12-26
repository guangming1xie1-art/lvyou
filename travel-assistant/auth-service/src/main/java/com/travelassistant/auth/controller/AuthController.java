package com.travelassistant.auth.controller;

import com.travelassistant.auth.service.JwtService;
import com.travelassistant.common.api.ApiResponse;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@Validated
public class AuthController {
  private final JwtService jwtService;

  public AuthController(JwtService jwtService) {
    this.jwtService = jwtService;
  }

  @PostMapping("/login")
  public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
    // MVP: 不接入用户表，仅返回一个可用 JWT
    String token = jwtService.generateToken(request.username);
    return ApiResponse.success(new LoginResponse(token));
  }

  public static class LoginRequest {
    @NotBlank
    public String username;

    @NotBlank
    public String password;
  }

  public record LoginResponse(String token) {
  }
}
