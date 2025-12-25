package com.travel.assistant.common.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 结果状态码枚举
 */
@Getter
@AllArgsConstructor
public enum ResultCode {

    SUCCESS(200, "操作成功"),
    FAIL(500, "操作失败"),

    // 认证相关 1001-1010
    UNAUTHORIZED(1001, "未登录或登录已过期"),
    FORBIDDEN(1002, "没有操作权限"),
    TOKEN_INVALID(1003, "Token无效"),
    TOKEN_EXPIRED(1004, "Token已过期"),

    // 参数相关 1001-1020
    PARAM_ERROR(1010, "参数错误"),
    PARAM_MISSING(1011, "参数缺失"),
    PARAM_INVALID(1012, "参数无效"),

    // 用户相关 2001-2010
    USER_NOT_FOUND(2001, "用户不存在"),
    USER_PASSWORD_ERROR(2002, "密码错误"),
    USER_DISABLED(2003, "用户已被禁用"),
    USER_EXISTS(2004, "用户已存在"),

    // 服务相关 3001-3010
    SERVICE_UNAVAILABLE(3001, "服务不可用"),
    SERVICE_ERROR(3002, "服务异常");

    private final Integer code;
    private final String message;
}
