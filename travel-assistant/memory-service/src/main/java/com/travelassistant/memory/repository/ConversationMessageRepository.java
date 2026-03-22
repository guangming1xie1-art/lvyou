package com.travelassistant.memory.repository;

import com.travelassistant.memory.entity.ConversationMessage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 对话消息Repository
 */
@Repository
public interface ConversationMessageRepository extends JpaRepository<ConversationMessage, UUID> {

    /**
     * 根据会话ID获取消息列表
     */
    @Query("SELECT m FROM ConversationMessage m WHERE m.conversationId = :conversationId " +
           "ORDER BY m.createdAt DESC")
    List<ConversationMessage> findByConversationIdOrderByCreatedAtDesc(@Param("conversationId") UUID conversationId);

    /**
     * 根据会话ID和用户ID获取消息列表（分页）
     */
    @Query("SELECT m FROM ConversationMessage m WHERE m.conversationId = :conversationId " +
           "AND m.userId = :userId " +
           "ORDER BY m.createdAt DESC")
    List<ConversationMessage> findByConversationIdAndUserId(@Param("conversationId") UUID conversationId,
                                                         @Param("userId") Long userId);

    /**
     * 统计会话的消息数量
     */
    @Query("SELECT COUNT(m) FROM ConversationMessage m WHERE m.conversationId = :conversationId")
    long countByConversationId(@Param("conversationId") UUID conversationId);

    /**
     * 根据会话ID删除消息
     */
    void deleteByConversationId(UUID conversationId);
}
