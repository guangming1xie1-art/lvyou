package com.travelassistant.user.repository;

import com.travelassistant.user.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface UserRepository extends JpaRepository<User, UUID> {

  /**
   * 根据邮箱查找用户
   */
  Optional<User> findByEmail(String email);

  /**
   * 根据用户名查找用户
   */
  Optional<User> findByUsername(String username);

  /**
   * 检查邮箱是否存在
   */
  @Query("SELECT CASE WHEN COUNT(u) > 0 THEN true ELSE false END FROM User u WHERE u.email = :email")
  boolean existsByEmail(@Param("email") String email);

  /**
   * 检查用户名是否存在
   */
  @Query("SELECT CASE WHEN COUNT(u) > 0 THEN true ELSE false END FROM User u WHERE u.username = :username")
  boolean existsByUsername(@Param("username") String username);
}