package com.travelassistant.auth.service;

import com.travelassistant.auth.config.JwtProperties;
import com.travelassistant.common.util.JwtUtil;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.concurrent.TimeUnit;

@Slf4j
@Service
@RequiredArgsConstructor
public class TokenBlacklistService {
    
    private static final String BLACKLIST_PREFIX = "blacklist:token:";
    
    private final RedisTemplate<String, Object> redisTemplate;
    private final JwtProperties jwtProperties;
    
    public void addToBlacklist(String token, Long userId) {
        try {
            LocalDateTime expiresAt = getTokenExpiration(token);
            long ttlSeconds = calculateTtlSeconds(expiresAt);
            
            if (ttlSeconds <= 0) {
                log.info("Token already expired, skipping blacklist");
                return;
            }
            
            String key = generateKey(token);
            redisTemplate.opsForValue().set(key, userId.toString(), ttlSeconds, TimeUnit.SECONDS);
            log.info("Token added to Redis blacklist for user: {}, TTL: {}s", userId, ttlSeconds);
            
        } catch (Exception e) {
            log.error("Failed to add token to blacklist: {}", e.getMessage());
            throw new RuntimeException("Failed to blacklist token", e);
        }
    }
    
    public boolean isBlacklisted(String token) {
        if (token == null || token.isBlank()) {
            return false;
        }
        
        try {
            String key = generateKey(token);
            return Boolean.TRUE.equals(redisTemplate.hasKey(key));
        } catch (Exception e) {
            log.error("Failed to check token blacklist: {}", e.getMessage());
            return false;
        }
    }
    
    private String generateKey(String token) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(token.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return BLACKLIST_PREFIX + hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            return BLACKLIST_PREFIX + token.hashCode();
        }
    }
    
    private long calculateTtlSeconds(LocalDateTime expiresAt) {
        LocalDateTime now = LocalDateTime.now();
        if (expiresAt.isBefore(now)) {
            return 0;
        }
        return Duration.between(now, expiresAt).getSeconds();
    }
    
    private LocalDateTime getTokenExpiration(String token) throws Exception {
        Claims claims = JwtUtil.getClaimsFromToken(token);
        Date expiration = claims.getExpiration();
        return expiration.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
    }
}
