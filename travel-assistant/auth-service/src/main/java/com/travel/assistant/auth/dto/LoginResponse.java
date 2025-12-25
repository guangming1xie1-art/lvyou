package com.travel.assistant.auth.dto;

import lombok.Builder;
import lombok.Data;

import java.io.Serializable;

/**
 * 登录响应
 */
@Data
@Builder
public class LoginResponse implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 访问令牌
     */
    private String accessToken;

    /**
     * 令牌类型
     */
    private String tokenType;

    /**
     * 刷新令牌
     */
    private String refreshToken;

    /**
     * 过期时间（秒）
     */
    private Long expiresIn;

    /**
     * 用户信息
     */
    private UserDTO user;

    @Data
    @Builder
    public static class UserDTO implements Serializable {
        private static final long serialVersionUID = 1L;
        private Long id;
        private String username;
        private String nickname;
        private String email;
        private String avatar;
        private String role;
    }
}
