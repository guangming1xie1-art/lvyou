package com.travelassistant.admin.service;

import com.travelassistant.admin.dto.UserDTOs;
import com.travelassistant.admin.entity.AdminUser;
import com.travelassistant.admin.entity.AdminUserRole;
import com.travelassistant.admin.entity.Role;
import com.travelassistant.admin.repository.AdminUserRepository;
import com.travelassistant.admin.repository.AdminUserRoleRepository;
import com.travelassistant.admin.repository.RoleRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final AdminUserRepository adminUserRepository;
    private final AdminUserRoleRepository adminUserRoleRepository;
    private final RoleRepository roleRepository;
    private final PasswordEncoder passwordEncoder;

    public Page<UserDTOs.UserResponse> getUsers(String keyword, Boolean status, Pageable pageable) {
        return adminUserRepository.findByKeywordAndStatus(keyword, status, pageable)
                .map(this::convertToUserResponse);
    }

    public UserDTOs.UserResponse getUser(Long id) {
        AdminUser user = adminUserRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found: " + id));
        return convertToUserResponse(user);
    }

    @Transactional
    public UserDTOs.UserResponse createUser(UserDTOs.UserRequest request) {
        if (adminUserRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("Username already exists");
        }
        if (adminUserRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email already exists");
        }

        AdminUser user = AdminUser.builder()
                .username(request.getUsername())
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .realName(request.getRealName())
                .phone(request.getPhone())
                .isActive(request.getIsActive() != null ? request.getIsActive() : true)
                .build();

        AdminUser saved = adminUserRepository.save(user);

        // 分配角色
        if (request.getRoleIds() != null) {
            for (Long roleId : request.getRoleIds()) {
                AdminUserRole userRole = AdminUserRole.builder()
                        .userId(saved.getId())
                        .roleId(roleId)
                        .build();
                adminUserRoleRepository.save(userRole);
            }
        }

        return convertToUserResponse(saved);
    }

    @Transactional
    public UserDTOs.UserResponse updateUser(Long id, UserDTOs.UserRequest request) {
        AdminUser user = adminUserRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found: " + id));

        if (request.getRealName() != null) {
            user.setRealName(request.getRealName());
        }
        if (request.getPhone() != null) {
            user.setPhone(request.getPhone());
        }
        if (request.getIsActive() != null) {
            user.setIsActive(request.getIsActive());
        }

        AdminUser updated = adminUserRepository.save(user);

        // 更新角色
        if (request.getRoleIds() != null) {
            adminUserRoleRepository.deleteByUserId(id);
            for (Long roleId : request.getRoleIds()) {
                AdminUserRole userRole = AdminUserRole.builder()
                        .userId(id)
                        .roleId(roleId)
                        .build();
                adminUserRoleRepository.save(userRole);
            }
        }

        return convertToUserResponse(updated);
    }

    @Transactional
    public void deleteUser(Long id) {
        adminUserRoleRepository.deleteByUserId(id);
        adminUserRepository.deleteById(id);
    }

    private UserDTOs.UserResponse convertToUserResponse(AdminUser user) {
        List<String> roles = adminUserRoleRepository.findByUserId(user.getId()).stream()
                .map(ur -> roleRepository.findById(ur.getRoleId())
                        .map(Role::getName)
                        .orElse(""))
                .collect(Collectors.toList());

        return UserDTOs.UserResponse.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .realName(user.getRealName())
                .phone(user.getPhone())
                .avatar(user.getAvatar())
                .isActive(user.getIsActive())
                .lastLogin(user.getLastLogin())
                .createdAt(user.getCreatedAt())
                .roles(roles)
                .build();
    }
}
