package com.travelassistant.memory.repository;

import com.travelassistant.memory.entity.Conversation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 对话会话Repository
 */
@Repository
public interface ConversationRepository extends JpaRepository<Conversation, UUID> {

    /**
     * 根据用户ID获取会话列表
     */
    @Query("SELECT c FROM Conversation c WHERE c.userId = :userId " +
           "AND (:status IS NULL OR c.status = :status) " +
           "ORDER BY c.updatedAt DESC")
    List<Conversation> findByUserId(@Param("userId") Long userId, 
                                   @Param("status") String status);

    /**
     * 根据会话ID获取会话
     */
    Optional<Conversation> findBySessionId(String sessionId);

    /**
     * 根据用户ID和会话ID获取会话
     */
    @Query("SELECT c FROM Conversation c WHERE c.userId = :userId AND c.sessionId = :sessionId")
    Optional<Conversation> findByUserIdAndSessionId(@Param("userId") Long userId, 
                                                 @Param("sessionId") String sessionId);

    /**
     * 根据用户ID删除会话
     */
    void deleteByUserId(Long userId);

    /**
     * 根据状态删除过期的会话
     */
    @Query("DELETE FROM Conversation c WHERE c.status = :status AND c.updatedAt < :expiryDate")
    void deleteByStatusAndUpdatedAtBefore(@Param("status") String status, 
                                       @Param("expiryDate") java.time.LocalDateTime expiryDate);
}
