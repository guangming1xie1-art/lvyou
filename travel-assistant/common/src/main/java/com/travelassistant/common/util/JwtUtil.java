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
  private JwtUtil() {
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
