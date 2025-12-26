package com.travelassistant.auth.service;

import com.travelassistant.auth.config.JwtProperties;
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
    Duration ttl = jwtProperties.getTtl();

    return JwtUtil.generateToken(userId, claims, secret, ttl);
  }
}
