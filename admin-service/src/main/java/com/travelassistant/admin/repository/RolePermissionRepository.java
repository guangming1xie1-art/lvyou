package com.travelassistant.admin.repository;

import com.travelassistant.admin.entity.RolePermission;
import com.travelassistant.admin.entity.RolePermissionId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RolePermissionRepository extends JpaRepository<RolePermission, RolePermissionId> {

    List<RolePermission> findByRoleId(Long roleId);

    List<RolePermission> findByPermissionId(Long permissionId);

    void deleteByRoleId(Long roleId);
}
