package com.travel.assistant.common.utils;

import lombok.Data;

/**
 * 登录用户信息
 */
@Data
public class LoginUser {

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 用户名
     */
    private String username;

    /**
     * 角色
     */
    private String role;

    public LoginUser() {
    }

    public LoginUser(Long userId, String username, String role) {
        this.userId = userId;
        this.username = username;
        this.role = role;
    }

    public static LoginUser of(Long userId, String username, String role) {
        return new LoginUser(userId, username, role);
    }
}
