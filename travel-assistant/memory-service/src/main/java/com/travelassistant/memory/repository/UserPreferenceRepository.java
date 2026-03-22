package com.travelassistant.memory.repository;

import com.travelassistant.memory.entity.UserPreference;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 用户偏好Repository
 */
@Repository
public interface UserPreferenceRepository extends JpaRepository<UserPreference, UUID> {

    /**
     * 根据用户ID获取偏好列表
     */
    List<UserPreference> findByUserId(Long userId);

    /**
     * 根据用户ID和偏好类型获取偏好
     */
    Optional<UserPreference> findByUserIdAndPreferenceType(Long userId, String preferenceType);

    /**
     * 根据用户ID和偏好类型删除偏好
     */
    void deleteByUserIdAndPreferenceType(Long userId, String preferenceType);

    /**
     * 删除低置信度的偏好
     */
    @Query("DELETE FROM UserPreference p WHERE p.userId = :userId " +
           "AND p.confidence < :confidenceThreshold " +
           "AND p.updatedAt < :expiryDate")
    void deleteLowConfidencePreferences(@Param("userId") Long userId,
                                     @Param("confidenceThreshold") Float confidenceThreshold,
                                     @Param("expiryDate") java.time.LocalDateTime expiryDate);
}
