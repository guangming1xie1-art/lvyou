package com.travel.assistant.auth.service;

import com.travel.assistant.auth.dto.LoginRequest;
import com.travel.assistant.auth.dto.LoginResponse;
import com.travel.assistant.auth.dto.RegisterRequest;

/**
 * 认证服务接口
 */
public interface AuthService {

    /**
     * 用户登录
     */
    LoginResponse login(LoginRequest request);

    /**
     * 用户注册
     */
    Boolean register(RegisterRequest request);

    /**
     * 刷新令牌
     */
    LoginResponse refreshToken(String refreshToken);

    /**
     * 验证令牌
     */
    Boolean validateToken(String token);
}
