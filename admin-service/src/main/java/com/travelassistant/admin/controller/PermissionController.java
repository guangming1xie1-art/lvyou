package com.travelassistant.admin.controller;

import com.travelassistant.admin.dto.UserDTOs;
import com.travelassistant.admin.service.PermissionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/admin/permissions")
@RequiredArgsConstructor
@Slf4j
public class PermissionController {

    private final PermissionService permissionService;

    @GetMapping
    public ResponseEntity<List<UserDTOs.PermissionResponse>> getAllPermissions() {
        return ResponseEntity.ok(permissionService.getAllPermissions());
    }

    @GetMapping("/type/{type}")
    public ResponseEntity<List<UserDTOs.PermissionResponse>> getPermissionsByType(@PathVariable String type) {
        return ResponseEntity.ok(permissionService.getPermissionsByType(type));
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserDTOs.PermissionResponse> getPermission(@PathVariable Long id) {
        return ResponseEntity.ok(permissionService.getPermission(id));
    }

    @PostMapping
    public ResponseEntity<UserDTOs.PermissionResponse> createPermission(@RequestBody UserDTOs.PermissionRequest request) {
        return ResponseEntity.ok(permissionService.createPermission(request));
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserDTOs.PermissionResponse> updatePermission(
            @PathVariable Long id,
            @RequestBody UserDTOs.PermissionRequest request) {
        return ResponseEntity.ok(permissionService.updatePermission(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePermission(@PathVariable Long id) {
        permissionService.deletePermission(id);
        return ResponseEntity.ok().build();
    }
}
