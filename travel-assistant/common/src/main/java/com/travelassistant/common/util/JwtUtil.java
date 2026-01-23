package com.travelassistant.common.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.Map;

public final class JwtUtil {
  private static final String DEFAULT_SECRET_KEY = System.getenv("JWT_SECRET_KEY");
  private static final String DEFAULT_ALGORITHM = "HS256";

  private JwtUtil() {
  }

  /**
   * 验证JWT token并返回Claims（使用环境变量JWT_SECRET_KEY）
   */
  public static Claims verifyToken(String token) throws Exception {
    return verifyToken(token, DEFAULT_SECRET_KEY);
  }

  /**
   * 检查token是否过期
   */
  public static boolean isTokenExpired(Claims claims) {
    return claims.getExpiration().before(new Date());
  }

  /**
   * 提取用户ID（使用环境变量JWT_SECRET_KEY）
   */
  public static String getUserIdFromToken(String token) throws Exception {
    Claims claims = verifyToken(token);
    return claims.getSubject();
  }

  /**
   * 从token中提取用户名（使用环境变量JWT_SECRET_KEY）
   */
  public static String getUsernameFromToken(String token) throws Exception {
    Claims claims = verifyToken(token);
    return (String) claims.get("username");
  }

  /**
   * 从token中提取所有claims（使用环境变量JWT_SECRET_KEY）
   */
  public static Claims getClaimsFromToken(String token) throws Exception {
    return verifyToken(token);
  }

  public static String generateToken(
      String subject,
      Map<String, Object> claims,
      String secret,
      Duration ttl
  ) {
    SecretKey key = key(secret);

    Instant now = Instant.now();
    Instant exp = ttl == null ? now.plus(Duration.ofHours(12)) : now.plus(ttl);

    return Jwts.builder()
        .setSubject(subject)
        .addClaims(claims)
        .setIssuedAt(Date.from(now))
        .setExpiration(Date.from(exp))
        .signWith(key, SignatureAlgorithm.HS256)
        .compact();
  }

  public static Claims parseClaims(String token, String secret) {
    SecretKey key = key(secret);
    return Jwts.parserBuilder()
        .setSigningKey(key)
        .build()
        .parseClaimsJws(token)
        .getBody();
  }

  public static String getUserIdFromToken(String token, String secret) {
    Claims claims = parseClaims(token, secret);
    return claims.getSubject();
  }

  public static Claims verifyToken(String token, String secret) throws Exception {
    return parseClaims(token, secret);
  }

  private static SecretKey key(String secret) {
    if (secret == null || secret.isBlank()) {
      throw new IllegalArgumentException("JWT secret must not be blank");
    }

    byte[] bytes = secret.getBytes(StandardCharsets.UTF_8);
    if (bytes.length < 32) {
      throw new IllegalArgumentException("JWT secret must be at least 32 bytes (256 bits) for HS256");
    }

    return Keys.hmacShaKeyFor(bytes);
  }
}
