package com.travelassistant.memory.service;

import com.travelassistant.memory.dto.ConversationDetail;
import com.travelassistant.memory.dto.MessageList;
import com.travelassistant.memory.dto.SessionStats;
import com.travelassistant.memory.entity.Conversation;
import com.travelassistant.memory.entity.ConversationMessage;
import com.travelassistant.memory.repository.ConversationMessageRepository;
import com.travelassistant.memory.repository.ConversationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 对话会话服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ConversationService {

    private final ConversationRepository conversationRepository;
    private final ConversationMessageRepository messageRepository;

    /**
     * 创建会话
     */
    @Transactional
    public Conversation createConversation(Long userId, String sessionId, String title, Map<String, Object> metadata) {
        Conversation conversation = new Conversation();
        conversation.setUserId(userId);
        conversation.setSessionId(sessionId);
        conversation.setTitle(title);
        conversation.setStatus("active");
        conversation.setMetadata(metadata != null ? metadata : new HashMap<>());
        
        Conversation saved = conversationRepository.save(conversation);
        log.info("Created conversation: {} for user: {}", sessionId, userId);
        
        return saved;
    }

    /**
     * 获取会话详情
     */
    public ConversationDetail getConversationDetail(Long userId, String sessionId) {
        Conversation conversation = conversationRepository.findByUserIdAndSessionId(userId, sessionId)
                .orElseThrow(() -> new RuntimeException("Conversation not found"));
        
        // 获取消息数量
        long messageCount = messageRepository.countByConversationId(conversation.getId());
        
        return ConversationDetail.builder()
                .conversation(conversation)
                .messageCount((int) messageCount)
                .build();
    }

    /**
     * 获取用户会话列表
     */
    public java.util.List<Conversation> getUserConversations(Long userId, Integer limit, String status) {
        return conversationRepository.findByUserId(userId, status).stream()
                .limit(limit)
                .toList();
    }

    /**
     * 更新会话摘要
     */
    @Transactional
    public void updateSummary(Long userId, String sessionId, String summary) {
        Conversation conversation = conversationRepository.findByUserIdAndSessionId(userId, sessionId)
                .orElseThrow(() -> new RuntimeException("Conversation not found"));
        
        conversation.setSummary(summary);
        conversationRepository.save(conversation);
        
        log.info("Updated summary for conversation: {}", sessionId);
    }

    /**
     * 归档会话
     */
    @Transactional
    public boolean archiveConversation(Long userId, String sessionId) {
        Conversation conversation = conversationRepository.findByUserIdAndSessionId(userId, sessionId)
                .orElseThrow(() -> new RuntimeException("Conversation not found"));
        
        conversation.setStatus("archived");
        conversation.setExpiresAt(LocalDateTime.now().plusDays(30));
        conversationRepository.save(conversation);
        
        log.info("Archived conversation: {}", sessionId);
        return true;
    }

    /**
     * 删除会话
     */
    @Transactional
    public void deleteConversation(Long userId, String sessionId) {
        Conversation conversation = conversationRepository.findByUserIdAndSessionId(userId, sessionId)
                .orElseThrow(() -> new RuntimeException("Conversation not found"));
        
        conversationRepository.delete(conversation);
        log.info("Deleted conversation: {}", sessionId);
    }

    /**
     * 获取会话统计
     */
    public SessionStats getSessionStats(Long userId, String sessionId) {
        Conversation conversation = conversationRepository.findByUserIdAndSessionId(userId, sessionId)
                .orElseThrow(() -> new RuntimeException("Conversation not found"));
        
        long messageCount = messageRepository.countByConversationId(conversation.getId());
        
        // 估算token数量（简单估算：中文约1.5字符/token）
        long totalTokens = (long) (messageCount * 100 * 1.5);
        
        boolean needsReset = messageCount > 50 || totalTokens > 80000;
        
        String resetReason = null;
        if (messageCount > 50) {
            resetReason = "对话轮数超过50轮，建议开始新会话";
        } else if (totalTokens > 80000) {
            resetReason = "对话内容较长，建议开始新会话以获得更好体验";
        }
        
        return SessionStats.builder()
                .sessionId(sessionId)
                .messageCount((int) messageCount)
                .totalTokens(totalTokens)
                .createdAt(conversation.getCreatedAt())
                .updatedAt(conversation.getUpdatedAt())
                .needsReset(needsReset)
                .resetReason(resetReason)
                .build();
    }

    /**
     * 重置会话
     */
    @Transactional
    public String resetSession(Long userId, String sessionId, boolean keepSummary) {
        Conversation oldConversation = conversationRepository.findByUserIdAndSessionId(userId, sessionId)
                .orElseThrow(() -> new RuntimeException("Conversation not found"));
        
        // 归档旧会话
        oldConversation.setStatus("archived");
        oldConversation.setExpiresAt(LocalDateTime.now().plusDays(30));
        conversationRepository.save(oldConversation);
        
        // 创建新会话
        String newSessionId = UUID.randomUUID().toString();
        String title = keepSummary && oldConversation.getSummary() != null 
                ? oldConversation.getTitle() + " (续)" 
                : "新对话";
        
        Conversation newConversation = new Conversation();
        newConversation.setUserId(userId);
        newConversation.setSessionId(newSessionId);
        newConversation.setTitle(title);
        newConversation.setStatus("active");
        newConversation.setMetadata(oldConversation.getMetadata());
        
        conversationRepository.save(newConversation);
        
        log.info("Reset session: {} -> {}", sessionId, newSessionId);
        return newSessionId;
    }
}
