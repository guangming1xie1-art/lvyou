package com.travelassistant.user.controller;

import com.travelassistant.user.entity.User;
import com.travelassistant.user.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/user")
@Tag(name = "User Service", description = "用户管理相关的API")
public class UserController {

    @Autowired
    private UserService userService;

    @PostMapping
    @Operation(summary = "创建用户", description = "创建新的用户账户")
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {
        User createdUser = userService.createUser(user);
        return new ResponseEntity<>(createdUser, HttpStatus.CREATED);
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取用户", description = "根据ID获取用户信息")
    public ResponseEntity<User> getUserById(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID id) {
        User user = userService.getUserById(id);
        return ResponseEntity.ok(user);
    }

    @GetMapping("/email/{email}")
    @Operation(summary = "获取用户（通过邮箱）", description = "根据邮箱获取用户信息")
    public ResponseEntity<User> getUserByEmail(
            @Parameter(description = "邮箱地址", required = true)
            @PathVariable @NotBlank String email) {
        User user = userService.getUserByEmail(email);
        return ResponseEntity.ok(user);
    }

    @GetMapping("/username/{username}")
    @Operation(summary = "获取用户（通过用户名）", description = "根据用户名获取用户信息")
    public ResponseEntity<User> getUserByUsername(
            @Parameter(description = "用户名", required = true)
            @PathVariable @NotBlank String username) {
        User user = userService.getUserByUsername(username);
        return ResponseEntity.ok(user);
    }

    @GetMapping
    @Operation(summary = "获取所有用户", description = "获取所有用户的列表")
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.getAllUsers();
        return ResponseEntity.ok(users);
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新用户", description = "更新指定ID的用户信息")
    public ResponseEntity<User> updateUser(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID id,
            @Valid @RequestBody User user) {
        User updatedUser = userService.updateUser(id, user);
        return ResponseEntity.ok(updatedUser);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除用户", description = "删除指定ID的用户")
    public ResponseEntity<Void> deleteUser(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/{id}/preferences")
    @Operation(summary = "获取用户偏好", description = "获取指定用户的偏好设置")
    public ResponseEntity<Map<String, Object>> getUserPreferences(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID id) {
        Map<String, Object> preferences = userService.getUserPreferences(id);
        return ResponseEntity.ok(preferences);
    }

    @PutMapping("/{id}/preferences")
    @Operation(summary = "更新用户偏好", description = "更新指定用户的偏好设置")
    public ResponseEntity<User> updateUserPreferences(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID id,
            @RequestBody Map<String, Object> preferences) {
        User user = userService.updateUserPreferences(id, preferences);
        return ResponseEntity.ok(user);
    }

    @PutMapping("/{id}/budget")
    @Operation(summary = "更新预算等级", description = "更新用户的预算等级")
    public ResponseEntity<User> updateBudgetLevel(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID id,
            @RequestParam @NotBlank String budgetLevel) {
        User user = userService.updateBudgetLevel(id, budgetLevel);
        return ResponseEntity.ok(user);
    }

    @PutMapping("/{id}/travel-style")
    @Operation(summary = "更新旅游风格", description = "更新用户的旅游风格偏好")
    public ResponseEntity<User> updateTravelStyle(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID id,
            @RequestParam @NotBlank String travelStyle) {
        User user = userService.updateTravelStyle(id, travelStyle);
        return ResponseEntity.ok(user);
    }

    @PutMapping("/{id}/interests")
    @Operation(summary = "更新用户兴趣", description = "更新用户的兴趣列表")
    public ResponseEntity<User> updateInterests(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID id,
            @RequestBody List<String> interests) {
        User user = userService.updateInterests(id, interests);
        return ResponseEntity.ok(user);
    }

    @PutMapping("/{id}/destinations")
    @Operation(summary = "更新偏好目的地", description = "更新用户的偏好目的地列表")
    public ResponseEntity<User> updatePreferredDestinations(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID id,
            @RequestBody List<String> destinations) {
        User user = userService.updatePreferredDestinations(id, destinations);
        return ResponseEntity.ok(user);
    }

    @GetMapping("/exists/email/{email}")
    @Operation(summary = "检查邮箱是否存在", description = "检查指定邮箱是否已被注册")
    public ResponseEntity<Boolean> checkEmailExists(
            @Parameter(description = "邮箱地址", required = true)
            @PathVariable String email) {
        boolean exists = userService.emailExists(email);
        return ResponseEntity.ok(exists);
    }

    @GetMapping("/exists/username/{username}")
    @Operation(summary = "检查用户名是否存在", description = "检查指定用户名是否已被注册")
    public ResponseEntity<Boolean> checkUsernameExists(
            @Parameter(description = "用户名", required = true)
            @PathVariable String username) {
        boolean exists = userService.usernameExists(username);
        return ResponseEntity.ok(exists);
    }
}