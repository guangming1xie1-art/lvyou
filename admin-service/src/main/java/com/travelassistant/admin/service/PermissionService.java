package com.travelassistant.admin.service;

import com.travelassistant.admin.dto.UserDTOs;
import com.travelassistant.admin.entity.Permission;
import com.travelassistant.admin.repository.PermissionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class PermissionService {

    private final PermissionRepository permissionRepository;

    public List<UserDTOs.PermissionResponse> getAllPermissions() {
        return permissionRepository.findAll().stream()
                .map(this::convertToPermissionResponse)
                .collect(Collectors.toList());
    }

    public List<UserDTOs.PermissionResponse> getPermissionsByType(String type) {
        return permissionRepository.findByType(type).stream()
                .map(this::convertToPermissionResponse)
                .collect(Collectors.toList());
    }

    public UserDTOs.PermissionResponse getPermission(Long id) {
        Permission permission = permissionRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Permission not found: " + id));
        return convertToPermissionResponse(permission);
    }

    @Transactional
    public UserDTOs.PermissionResponse createPermission(UserDTOs.PermissionRequest request) {
        if (permissionRepository.existsByCode(request.getCode())) {
            throw new RuntimeException("Permission code already exists");
        }

        Permission permission = Permission.builder()
                .name(request.getName())
                .code(request.getCode())
                .type(request.getType())
                .parentId(request.getParentId())
                .path(request.getPath())
                .icon(request.getIcon())
                .sortOrder(request.getSortOrder() != null ? request.getSortOrder() : 0)
                .isActive(request.getIsActive() != null ? request.getIsActive() : true)
                .build();

        Permission saved = permissionRepository.save(permission);
        return convertToPermissionResponse(saved);
    }

    @Transactional
    public UserDTOs.PermissionResponse updatePermission(Long id, UserDTOs.PermissionRequest request) {
        Permission permission = permissionRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Permission not found: " + id));

        permission.setName(request.getName());
        permission.setType(request.getType());
        permission.setParentId(request.getParentId());
        permission.setPath(request.getPath());
        permission.setIcon(request.getIcon());
        if (request.getSortOrder() != null) {
            permission.setSortOrder(request.getSortOrder());
        }
        if (request.getIsActive() != null) {
            permission.setIsActive(request.getIsActive());
        }

        Permission updated = permissionRepository.save(permission);
        return convertToPermissionResponse(updated);
    }

    @Transactional
    public void deletePermission(Long id) {
        permissionRepository.deleteById(id);
    }

    private UserDTOs.PermissionResponse convertToPermissionResponse(Permission permission) {
        return UserDTOs.PermissionResponse.builder()
                .id(permission.getId())
                .name(permission.getName())
                .code(permission.getCode())
                .type(permission.getType())
                .parentId(permission.getParentId())
                .path(permission.getPath())
                .icon(permission.getIcon())
                .sortOrder(permission.getSortOrder())
                .isActive(permission.getIsActive())
                .createdAt(permission.getCreatedAt())
                .build();
    }
}
