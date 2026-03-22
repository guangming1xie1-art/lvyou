package com.travelassistant.memory.repository;

import com.travelassistant.memory.entity.VectorMemory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 向量记忆Repository
 */
@Repository
public interface VectorMemoryRepository extends JpaRepository<VectorMemory, UUID> {

    /**
     * 根据用户ID获取向量记忆列表
     */
    List<VectorMemory> findByUserId(Long userId);

    /**
     * 根据用户ID和记忆类型获取向量记忆
     */
    @Query("SELECT v FROM VectorMemory v WHERE v.userId = :userId " +
           "AND (:memoryType IS NULL OR v.memoryType = :memoryType) " +
           "ORDER BY v.createdAt DESC")
    List<VectorMemory> findByUserIdAndMemoryType(@Param("userId") Long userId,
                                              @Param("memoryType") String memoryType);

    /**
     * 根据用户ID删除向量记忆
     */
    void deleteByUserId(Long userId);

    /**
     * 根据记忆类型删除向量记忆
     */
    void deleteByMemoryType(String memoryType);
}
