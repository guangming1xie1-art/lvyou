package com.travelassistant.user.service;

import com.travelassistant.user.entity.User;
import com.travelassistant.user.repository.UserRepository;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@Transactional
public class UserService {

    @Autowired
    private UserRepository userRepository;

    /**
     * 创建用户
     */
    public User createUser(User user) {
        // 验证邮箱唯一性
        if (userRepository.existsByEmail(user.getEmail())) {
            throw new IllegalArgumentException("Email already exists: " + user.getEmail());
        }
        
        // 验证用户名唯一性
        if (userRepository.existsByUsername(user.getUsername())) {
            throw new IllegalArgumentException("Username already exists: " + user.getUsername());
        }

        // 设置默认值
        if (user.getPreferencesJson() == null) {
            user.setPreferencesJson(new HashMap<>());
        }

        return userRepository.save(user);
    }

    /**
     * 根据ID获取用户
     */
    public User getUserById(UUID id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("User not found with id: " + id));
    }

    /**
     * 根据邮箱获取用户
     */
    public User getUserByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new EntityNotFoundException("User not found with email: " + email));
    }

    /**
     * 根据用户名获取用户
     */
    public User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new EntityNotFoundException("User not found with username: " + username));
    }

    /**
     * 获取所有用户
     */
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    /**
     * 更新用户
     */
    public User updateUser(UUID id, User updatedUser) {
        User existingUser = getUserById(id);
        
        // 检查邮箱唯一性（排除当前用户）
        if (!existingUser.getEmail().equals(updatedUser.getEmail()) && 
            userRepository.existsByEmail(updatedUser.getEmail())) {
            throw new IllegalArgumentException("Email already exists: " + updatedUser.getEmail());
        }
        
        // 检查用户名唯一性（排除当前用户）
        if (!existingUser.getUsername().equals(updatedUser.getUsername()) && 
            userRepository.existsByUsername(updatedUser.getUsername())) {
            throw new IllegalArgumentException("Username already exists: " + updatedUser.getUsername());
        }

        // 更新字段
        existingUser.setEmail(updatedUser.getEmail());
        existingUser.setUsername(updatedUser.getUsername());
        existingUser.setPreferencesJson(updatedUser.getPreferencesJson());
        existingUser.setUpdatedAt(LocalDateTime.now());

        return userRepository.save(existingUser);
    }

    /**
     * 删除用户
     */
    public void deleteUser(UUID id) {
        User user = getUserById(id);
        userRepository.delete(user);
    }

    /**
     * 更新用户偏好
     */
    public User updateUserPreferences(UUID id, Map<String, Object> preferences) {
        User user = getUserById(id);
        if (user.getPreferencesJson() == null) {
            user.setPreferencesJson(new HashMap<>());
        }
        user.getPreferencesJson().putAll(preferences);
        user.setUpdatedAt(LocalDateTime.now());
        return userRepository.save(user);
    }

    /**
     * 获取用户偏好
     */
    public Map<String, Object> getUserPreferences(UUID id) {
        User user = getUserById(id);
        return user.getPreferencesJson() != null ? user.getPreferencesJson() : new HashMap<>();
    }

    /**
     * 更新用户预算等级
     */
    public User updateBudgetLevel(UUID id, String budgetLevel) {
        User user = getUserById(id);
        Map<String, Object> preferences = user.getPreferencesJson();
        if (preferences == null) {
            preferences = new HashMap<>();
            user.setPreferencesJson(preferences);
        }
        preferences.put("budget_level", budgetLevel);
        user.setUpdatedAt(LocalDateTime.now());
        return userRepository.save(user);
    }

    /**
     * 更新用户旅游风格
     */
    public User updateTravelStyle(UUID id, String travelStyle) {
        User user = getUserById(id);
        Map<String, Object> preferences = user.getPreferencesJson();
        if (preferences == null) {
            preferences = new HashMap<>();
            user.setPreferencesJson(preferences);
        }
        preferences.put("travel_style", travelStyle);
        user.setUpdatedAt(LocalDateTime.now());
        return userRepository.save(user);
    }

    /**
     * 更新用户兴趣
     */
    public User updateInterests(UUID id, List<String> interests) {
        User user = getUserById(id);
        Map<String, Object> preferences = user.getPreferencesJson();
        if (preferences == null) {
            preferences = new HashMap<>();
            user.setPreferencesJson(preferences);
        }
        preferences.put("interests", interests);
        user.setUpdatedAt(LocalDateTime.now());
        return userRepository.save(user);
    }

    /**
     * 更新用户偏好目的地
     */
    public User updatePreferredDestinations(UUID id, List<String> destinations) {
        User user = getUserById(id);
        Map<String, Object> preferences = user.getPreferencesJson();
        if (preferences == null) {
            preferences = new HashMap<>();
            user.setPreferencesJson(preferences);
        }
        preferences.put("preferred_destinations", destinations);
        user.setUpdatedAt(LocalDateTime.now());
        return userRepository.save(user);
    }

    /**
     * 检查用户是否存在
     */
    public boolean userExists(UUID id) {
        return userRepository.existsById(id);
    }

    /**
     * 检查邮箱是否存在
     */
    public boolean emailExists(String email) {
        return userRepository.existsByEmail(email);
    }

    /**
     * 检查用户名是否存在
     */
    public boolean usernameExists(String username) {
        return userRepository.existsByUsername(username);
    }
}