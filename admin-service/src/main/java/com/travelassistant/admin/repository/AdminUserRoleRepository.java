package com.travelassistant.admin.repository;

import com.travelassistant.admin.entity.AdminUserRole;
import com.travelassistant.admin.entity.AdminUserRoleId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AdminUserRoleRepository extends JpaRepository<AdminUserRole, AdminUserRoleId> {

    List<AdminUserRole> findByUserId(Long userId);

    List<AdminUserRole> findByRoleId(Long roleId);

    void deleteByUserId(Long userId);
}
