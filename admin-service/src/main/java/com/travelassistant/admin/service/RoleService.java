package com.travelassistant.admin.service;

import com.travelassistant.admin.dto.UserDTOs;
import com.travelassistant.admin.entity.Role;
import com.travelassistant.admin.entity.RolePermission;
import com.travelassistant.admin.repository.PermissionRepository;
import com.travelassistant.admin.repository.RolePermissionRepository;
import com.travelassistant.admin.repository.RoleRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class RoleService {

    private final RoleRepository roleRepository;
    private final RolePermissionRepository rolePermissionRepository;
    private final PermissionRepository permissionRepository;

    public List<UserDTOs.RoleResponse> getAllRoles() {
        return roleRepository.findAll().stream()
                .map(this::convertToRoleResponse)
                .collect(Collectors.toList());
    }

    public UserDTOs.RoleResponse getRole(Long id) {
        Role role = roleRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Role not found: " + id));
        return convertToRoleResponse(role);
    }

    @Transactional
    public UserDTOs.RoleResponse createRole(UserDTOs.RoleRequest request) {
        if (roleRepository.existsByCode(request.getCode())) {
            throw new RuntimeException("Role code already exists");
        }

        Role role = Role.builder()
                .name(request.getName())
                .code(request.getCode())
                .description(request.getDescription())
                .isActive(request.getIsActive() != null ? request.getIsActive() : true)
                .build();

        Role saved = roleRepository.save(role);

        if (request.getPermissionIds() != null) {
            for (Long permissionId : request.getPermissionIds()) {
                RolePermission rp = RolePermission.builder()
                        .roleId(saved.getId())
                        .permissionId(permissionId)
                        .build();
                rolePermissionRepository.save(rp);
            }
        }

        return convertToRoleResponse(saved);
    }

    @Transactional
    public UserDTOs.RoleResponse updateRole(Long id, UserDTOs.RoleRequest request) {
        Role role = roleRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Role not found: " + id));

        role.setName(request.getName());
        role.setDescription(request.getDescription());
        if (request.getIsActive() != null) {
            role.setIsActive(request.getIsActive());
        }

        Role updated = roleRepository.save(role);

        if (request.getPermissionIds() != null) {
            rolePermissionRepository.deleteByRoleId(id);
            for (Long permissionId : request.getPermissionIds()) {
                RolePermission rp = RolePermission.builder()
                        .roleId(id)
                        .permissionId(permissionId)
                        .build();
                rolePermissionRepository.save(rp);
            }
        }

        return convertToRoleResponse(updated);
    }

    @Transactional
    public void deleteRole(Long id) {
        rolePermissionRepository.deleteByRoleId(id);
        roleRepository.deleteById(id);
    }

    private UserDTOs.RoleResponse convertToRoleResponse(Role role) {
        List<String> permissions = rolePermissionRepository.findByRoleId(role.getId()).stream()
                .map(rp -> permissionRepository.findById(rp.getPermissionId())
                        .map(p -> p.getName())
                        .orElse(""))
                .collect(Collectors.toList());

        return UserDTOs.RoleResponse.builder()
                .id(role.getId())
                .name(role.getName())
                .code(role.getCode())
                .description(role.getDescription())
                .isActive(role.getIsActive())
                .createdAt(role.getCreatedAt())
                .permissions(permissions)
                .build();
    }
}
