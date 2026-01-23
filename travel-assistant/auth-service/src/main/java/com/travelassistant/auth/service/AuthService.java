package com.travelassistant.auth.service;

import com.travelassistant.auth.dto.*;
import com.travelassistant.auth.entity.User;
import com.travelassistant.auth.repository.UserRepository;
import com.travelassistant.common.util.JwtUtil;
import io.jsonwebtoken.Claims;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Slf4j
@Service
public class AuthService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final com.travelassistant.auth.config.JwtProperties jwtProperties;

    public AuthService(UserRepository userRepository, 
                       PasswordEncoder passwordEncoder, 
                       JwtService jwtService,
                       com.travelassistant.auth.config.JwtProperties jwtProperties) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
        this.jwtProperties = jwtProperties;
    }

    public UserResponse register(RegisterRequest request) throws Exception {
        // 检查密码确认
        if (!request.getPassword().equals(request.getConfirmPassword())) {
            throw new IllegalArgumentException("Passwords do not match");
        }

        // 检查用户名和邮箱是否已存在
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new IllegalArgumentException("Username already exists");
        }
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Email already exists");
        }

        // 创建用户
        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPasswordHash(passwordEncoder.encode(request.getPassword()));
        user.setIsActive(true);

        User savedUser = userRepository.save(user);
        return convertToUserResponse(savedUser);
    }

    public LoginResponse login(LoginRequest request) throws Exception {
        User user = userRepository.findByUsername(request.getUsername())
            .orElseThrow(() -> new IllegalArgumentException("Invalid username or password"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Invalid username or password");
        }

        if (!user.getIsActive()) {
            throw new IllegalArgumentException("User account is disabled");
        }

        // 更新最后登录时间
        user.setLastLogin(LocalDateTime.now());
        userRepository.save(user);

        // 生成tokens
        String accessToken = jwtService.generateAccessToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);

        LoginResponse response = new LoginResponse(
            convertToUserResponse(user),
            new TokenResponse(
                accessToken,
                refreshToken,
                "Bearer",
                jwtProperties.getAccessTokenExpiration() / 1000
            )
        );

        return response;
    }

    public TokenResponse refreshToken(RefreshTokenRequest request) throws Exception {
        Claims claims = JwtUtil.verifyToken(request.getRefreshToken(), jwtProperties.getSecret());

        String userId = claims.getSubject();
        User user = userRepository.findById(Long.parseLong(userId))
            .orElseThrow(() -> new IllegalArgumentException("User not found"));

        if (!user.getIsActive()) {
            throw new IllegalArgumentException("User account is disabled");
        }

        String newAccessToken = jwtService.generateAccessToken(user);
        String newRefreshToken = jwtService.generateRefreshToken(user);

        return new TokenResponse(
            newAccessToken,
            newRefreshToken,
            "Bearer",
            jwtProperties.getAccessTokenExpiration() / 1000
        );
    }

    public UserResponse getCurrentUser(String userId) throws Exception {
        User user = userRepository.findById(Long.parseLong(userId))
            .orElseThrow(() -> new IllegalArgumentException("User not found"));
        return convertToUserResponse(user);
    }

    private UserResponse convertToUserResponse(User user) {
        return UserResponse.builder()
            .id(user.getId())
            .username(user.getUsername())
            .email(user.getEmail())
            .isActive(user.getIsActive())
            .createdAt(user.getCreatedAt())
            .lastLogin(user.getLastLogin())
            .build();
    }
}