package com.travelassistant.auth.service;

import com.travelassistant.auth.config.JwtProperties;
import com.travelassistant.auth.entity.User;
import com.travelassistant.common.util.JwtUtil;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

@Service
public class JwtService {
  private final JwtProperties jwtProperties;

  public JwtService(JwtProperties jwtProperties) {
    this.jwtProperties = jwtProperties;
  }

  public String generateToken(String userId) {
    Map<String, Object> claims = new HashMap<>();
    claims.put("userId", userId);

    String secret = jwtProperties.getSecret();
    Duration ttl = Duration.ofMillis(jwtProperties.getAccessTokenExpiration());

    return JwtUtil.generateToken(userId, claims, secret, ttl);
  }

  public String generateAccessToken(User user) {
    Map<String, Object> claims = new HashMap<>();
    claims.put("username", user.getUsername());
    claims.put("type", "access");

    return JwtUtil.generateToken(
        user.getId().toString(),
        claims,
        jwtProperties.getSecret(),
        Duration.ofMillis(jwtProperties.getAccessTokenExpiration())
    );
  }

  public String generateRefreshToken(User user) {
    Map<String, Object> claims = new HashMap<>();
    claims.put("username", user.getUsername());
    claims.put("type", "refresh");

    return JwtUtil.generateToken(
        user.getId().toString(),
        claims,
        jwtProperties.getSecret(),
        Duration.ofMillis(jwtProperties.getRefreshTokenExpiration())
    );
  }

  public String getUserIdFromToken(String token) throws Exception {
    return JwtUtil.getUserIdFromToken(token, jwtProperties.getSecret());
  }
}
