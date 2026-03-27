package com.travelassistant.auth.controller;

import com.travelassistant.auth.dto.AddBlacklistRequest;
import com.travelassistant.auth.service.JwtService;
import com.travelassistant.auth.service.TokenBlacklistService;
import com.travelassistant.common.api.ApiResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/auth/blacklist")
@Validated
@RequiredArgsConstructor
public class BlacklistController {
    
    private final TokenBlacklistService tokenBlacklistService;
    private final JwtService jwtService;
    
    @PostMapping("/add")
    public ApiResponse<String> addToBlacklist(
            @RequestHeader("Authorization") String authHeader,
            @RequestBody(required = false) AddBlacklistRequest request) {
        try {
            String token = authHeader.substring(7);
            Long userId = request != null && request.getUserId() != null 
                    ? request.getUserId() 
                    : Long.parseLong(jwtService.getUserIdFromToken(token));
            
            tokenBlacklistService.addToBlacklist(token, userId);
            return ApiResponse.success("Token added to blacklist");
        } catch (Exception e) {
            log.error("Failed to add token to blacklist: {}", e.getMessage());
            return ApiResponse.error(500, "Failed to add token to blacklist: " + e.getMessage());
        }
    }
    
    @GetMapping("/check")
    public ApiResponse<Map<String, Boolean>> checkBlacklist(
            @RequestHeader("Authorization") String authHeader) {
        try {
            String token = authHeader.substring(7);
            boolean isBlacklisted = tokenBlacklistService.isBlacklisted(token);
            return ApiResponse.success(Map.of("blacklisted", isBlacklisted));
        } catch (Exception e) {
            log.error("Failed to check token blacklist: {}", e.getMessage());
            return ApiResponse.success(Map.of("blacklisted", false));
        }
    }
}
