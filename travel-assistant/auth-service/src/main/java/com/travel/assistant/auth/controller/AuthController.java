package com.travel.assistant.auth.controller;

import com.travel.assistant.auth.dto.LoginRequest;
import com.travel.assistant.auth.dto.LoginResponse;
import com.travel.assistant.auth.dto.RegisterRequest;
import com.travel.assistant.auth.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

/**
 * 认证控制器
 */
@Tag(name = "认证管理", description = "用户登录、注册、令牌管理")
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @Operation(summary = "用户登录")
    @PostMapping("/login")
    public LoginResponse login(@Valid @RequestBody LoginRequest request) {
        return authService.login(request);
    }

    @Operation(summary = "用户注册")
    @PostMapping("/register")
    public Boolean register(@Valid @RequestBody RegisterRequest request) {
        return authService.register(request);
    }

    @Operation(summary = "刷新令牌")
    @PostMapping("/refresh")
    public LoginResponse refreshToken(@RequestHeader("Authorization") String refreshToken) {
        return authService.refreshToken(refreshToken);
    }

    @Operation(summary = "验证令牌")
    @GetMapping("/validate")
    public Boolean validateToken(@RequestHeader("Authorization") String token) {
        return authService.validateToken(token);
    }
}
