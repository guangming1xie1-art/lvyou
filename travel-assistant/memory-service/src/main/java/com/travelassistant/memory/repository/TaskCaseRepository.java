package com.travelassistant.memory.repository;

import com.travelassistant.memory.entity.TaskCase;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 任务案例Repository
 */
@Repository
public interface TaskCaseRepository extends JpaRepository<TaskCase, UUID> {

    /**
     * 根据用户ID获取任务案例列表
     */
    @Query("SELECT t FROM TaskCase t WHERE t.userId = :userId " +
           "AND (:destination IS NULL OR t.destination = :destination) " +
           "ORDER BY t.createdAt DESC")
    List<TaskCase> findByUserIdAndDestination(@Param("userId") Long userId,
                                           @Param("destination") String destination);

    /**
     * 根据用户ID和目的地获取任务案例
     */
    List<TaskCase> findByUserIdAndDestination(Long userId, String destination);

    /**
     * 根据用户ID删除任务案例
     */
    void deleteByUserId(Long userId);
}
