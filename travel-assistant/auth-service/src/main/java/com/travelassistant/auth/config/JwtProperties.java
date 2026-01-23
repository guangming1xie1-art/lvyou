package com.travelassistant.auth.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.time.Duration;

@ConfigurationProperties(prefix = "jwt")
public class JwtProperties {
  private String secret;
  private String algorithm = "HS256";
  private Long accessTokenExpiration = 900000L;    // 15分钟（毫秒）
  private Long refreshTokenExpiration = 604800000L; // 7天（毫秒）

  public String getSecret() {
    return secret;
  }

  public void setSecret(String secret) {
    this.secret = secret;
  }

  public String getAlgorithm() {
    return algorithm;
  }

  public void setAlgorithm(String algorithm) {
    this.algorithm = algorithm;
  }

  public Long getAccessTokenExpiration() {
    return accessTokenExpiration;
  }

  public void setAccessTokenExpiration(Long accessTokenExpiration) {
    this.accessTokenExpiration = accessTokenExpiration;
  }

  public Long getRefreshTokenExpiration() {
    return refreshTokenExpiration;
  }

  public void setRefreshTokenExpiration(Long refreshTokenExpiration) {
    this.refreshTokenExpiration = refreshTokenExpiration;
  }
}
