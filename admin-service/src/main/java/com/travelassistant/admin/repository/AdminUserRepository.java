package com.travelassistant.admin.repository;

import com.travelassistant.admin.entity.AdminUser;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AdminUserRepository extends JpaRepository<AdminUser, Long> {

    Optional<AdminUser> findByUsername(String username);

    Optional<AdminUser> findByEmail(String email);

    @Query("SELECT u FROM AdminUser u WHERE " +
           "(:keyword IS NULL OR u.username LIKE %:keyword% OR u.email LIKE %:keyword% OR u.realName LIKE %:keyword%) AND " +
           "(:status IS NULL OR u.isActive = :status)")
    Page<AdminUser> findByKeywordAndStatus(
            @Param("keyword") String keyword,
            @Param("status") Boolean status,
            Pageable pageable);

    boolean existsByUsername(String username);

    boolean existsByEmail(String email);
}
