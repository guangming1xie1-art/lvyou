package com.travelassistant.auth.controller;

import com.travelassistant.auth.dto.*;
import com.travelassistant.auth.service.AuthService;
import com.travelassistant.auth.service.JwtService;
import com.travelassistant.auth.service.TokenBlacklistService;
import com.travelassistant.common.api.ApiResponse;
import com.travelassistant.common.api.ResultCode;
import jakarta.validation.Valid;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@Validated
public class AuthController {
  private final AuthService authService;
  private final JwtService jwtService;
  private final TokenBlacklistService tokenBlacklistService;

  public AuthController(AuthService authService, JwtService jwtService, TokenBlacklistService tokenBlacklistService) {
    this.authService = authService;
    this.jwtService = jwtService;
    this.tokenBlacklistService = tokenBlacklistService;
  }

  @PostMapping("/register")
  public ApiResponse<UserResponse> register(@Valid @RequestBody RegisterRequest request) {
    try {
      UserResponse user = authService.register(request);
      return ApiResponse.success(user);
    } catch (Exception e) {
      return ApiResponse.error(ResultCode.UNAUTHORIZED.getCode(),e.getMessage());
    }
  }

  @PostMapping("/login")
  public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
    try {
      LoginResponse response = authService.login(request);
      return ApiResponse.success(response);
    } catch (Exception e) {
      return ApiResponse.error(ResultCode.UNAUTHORIZED.getCode(),e.getMessage());
    }
  }

  @PostMapping("/refresh")
  public ApiResponse<TokenResponse> refreshToken(@Valid @RequestBody RefreshTokenRequest request) {
    try {
      TokenResponse response = authService.refreshToken(request);
      return ApiResponse.success(response);
    } catch (Exception e) {
      return ApiResponse.error(ResultCode.UNAUTHORIZED.getCode(),e.getMessage());
    }
  }

  @GetMapping("/me")
  public ApiResponse<UserResponse> getCurrentUser(@RequestHeader("Authorization") String authHeader) {
    try {
      String token = authHeader.substring(7);
      String userId = jwtService.getUserIdFromToken(token);
      UserResponse user = authService.getCurrentUser(userId);
      return ApiResponse.success(user);
    } catch (Exception e) {
      return ApiResponse.error(ResultCode.UNAUTHORIZED.getCode(),"Failed to get current user: " + e.getMessage());
    }
  }

  @PostMapping("/logout")
  public ApiResponse<String> logout(@RequestHeader("Authorization") String authHeader) {
    try {
      String token = authHeader.substring(7);
      String userIdStr = jwtService.getUserIdFromToken(token);
      Long userId = Long.parseLong(userIdStr);
      
      tokenBlacklistService.addToBlacklist(token, userId);
      log.info("User {} logged out, token added to blacklist", userId);
      
      return ApiResponse.success("Logged out successfully");
    } catch (Exception e) {
      log.error("Logout failed: {}", e.getMessage());
      return ApiResponse.error(ResultCode.INTERNAL_SERVER_ERROR.getCode(), "Logout failed: " + e.getMessage());
    }
  }
}
