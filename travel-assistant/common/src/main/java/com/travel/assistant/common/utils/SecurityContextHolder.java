package com.travel.assistant.common.utils;

import lombok.extern.slf4j.Slf4j;

/**
 * 安全上下文持有者
 */
@Slf4j
public class SecurityContextHolder {

    private static final ThreadLocal<LoginUser> CONTEXT = new ThreadLocal<>();

    /**
     * 设置当前登录用户
     */
    public static void setCurrentUser(LoginUser user) {
        CONTEXT.set(user);
    }

    /**
     * 获取当前登录用户
     */
    public static LoginUser getCurrentUser() {
        return CONTEXT.get();
    }

    /**
     * 获取当前用户ID
     */
    public static Long getCurrentUserId() {
        LoginUser user = CONTEXT.get();
        return user != null ? user.getUserId() : null;
    }

    /**
     * 获取当前用户名
     */
    public static String getCurrentUsername() {
        LoginUser user = CONTEXT.get();
        return user != null ? user.getUsername() : null;
    }

    /**
     * 清空上下文
     */
    public static void clear() {
        CONTEXT.remove();
    }
}
