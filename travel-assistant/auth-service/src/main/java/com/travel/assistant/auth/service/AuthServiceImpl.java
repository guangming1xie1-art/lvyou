package com.travel.assistant.auth.service;

import cn.hutool.crypto.SecureUtil;
import com.travel.assistant.auth.dto.LoginRequest;
import com.travel.assistant.auth.dto.LoginResponse;
import com.travel.assistant.auth.dto.RegisterRequest;
import com.travel.assistant.auth.entity.User;
import com.travel.assistant.common.exception.BusinessException;
import com.travel.assistant.common.utils.JwtUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * 认证服务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final JwtUtils jwtUtils;

    @Value("${jwt.expiration:86400000}")
    private Long expiration;

    @Value("${jwt.refresh-expiration:604800000}")
    private Long refreshExpiration;

    // 模拟数据存储，实际应使用数据库
    private static final java.util.concurrent.ConcurrentHashMap<String, User> USER_MAP = new java.util.concurrent.ConcurrentHashMap<>();

    static {
        // 初始化测试用户
        User testUser = new User();
        testUser.setId(1L);
        testUser.setUsername("test");
        testUser.setPassword(SecureUtil.md5("123456"));
        testUser.setNickname("测试用户");
        testUser.setEmail("test@example.com");
        testUser.setStatus(1);
        testUser.setRole("USER");
        USER_MAP.put("test", testUser);
    }

    @Override
    public LoginResponse login(LoginRequest request) {
        User user = USER_MAP.get(request.getUsername());
        if (user == null) {
            throw new BusinessException("用户名或密码错误");
        }

        if (user.getStatus() == 0) {
            throw new BusinessException("用户已被禁用");
        }

        // 验证密码
        String encryptedPassword = SecureUtil.md5(request.getPassword());
        if (!encryptedPassword.equals(user.getPassword())) {
            throw new BusinessException("用户名或密码错误");
        }

        // 生成令牌
        String accessToken = jwtUtils.generateToken(user.getId(), user.getUsername());

        return LoginResponse.builder()
                .accessToken(accessToken)
                .tokenType("Bearer")
                .expiresIn(expiration / 1000)
                .user(LoginResponse.UserDTO.builder()
                        .id(user.getId())
                        .username(user.getUsername())
                        .nickname(user.getNickname())
                        .email(user.getEmail())
                        .avatar(user.getAvatar())
                        .role(user.getRole())
                        .build())
                .build();
    }

    @Override
    public Boolean register(RegisterRequest request) {
        // 检查用户名是否已存在
        if (USER_MAP.containsKey(request.getUsername())) {
            throw new BusinessException("用户名已存在");
        }

        // 验证两次密码是否一致
        if (!request.getPassword().equals(request.getConfirmPassword())) {
            throw new BusinessException("两次密码输入不一致");
        }

        // 创建新用户
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(SecureUtil.md5(request.getPassword()));
        user.setNickname(request.getNickname() != null ? request.getNickname() : request.getUsername());
        user.setEmail(request.getEmail());
        user.setStatus(1);
        user.setRole("USER");

        USER_MAP.put(user.getUsername(), user);
        return true;
    }

    @Override
    public LoginResponse refreshToken(String refreshToken) {
        // 简化处理，实际应使用Redis存储refreshToken
        if (!jwtUtils.validateToken(refreshToken)) {
            throw new BusinessException("刷新令牌无效");
        }

        Long userId = jwtUtils.getUserId(refreshToken);
        String username = jwtUtils.getUsername(refreshToken);
        String newAccessToken = jwtUtils.generateToken(userId, username);

        return LoginResponse.builder()
                .accessToken(newAccessToken)
                .tokenType("Bearer")
                .expiresIn(expiration / 1000)
                .build();
    }

    @Override
    public Boolean validateToken(String token) {
        return jwtUtils.validateToken(token);
    }
}
