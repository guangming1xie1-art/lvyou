package com.travelassistant.admin.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

public class UserDTOs {

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class UserRequest {
        private String email;
        private String username;
        private String password;
        private String realName;
        private String phone;
        private Boolean isActive;
        private List<Long> roleIds;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class UserResponse {
        private Long id;
        private String email;
        private String username;
        private String realName;
        private String phone;
        private String avatar;
        private Boolean isActive;
        private LocalDateTime lastLogin;
        private LocalDateTime createdAt;
        private List<String> roles;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class RoleRequest {
        private String name;
        private String code;
        private String description;
        private Boolean isActive;
        private List<Long> permissionIds;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class RoleResponse {
        private Long id;
        private String name;
        private String code;
        private String description;
        private Boolean isActive;
        private LocalDateTime createdAt;
        private List<String> permissions;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class PermissionRequest {
        private String name;
        private String code;
        private String type;
        private Long parentId;
        private String path;
        private String icon;
        private Integer sortOrder;
        private Boolean isActive;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class PermissionResponse {
        private Long id;
        private String name;
        private String code;
        private String type;
        private Long parentId;
        private String path;
        private String icon;
        private Integer sortOrder;
        private Boolean isActive;
        private LocalDateTime createdAt;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class LoginRequest {
        private String username;
        private String password;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class LoginResponse {
        private String token;
        private String type;
        private Long expiresIn;
        private UserResponse user;
    }
}
