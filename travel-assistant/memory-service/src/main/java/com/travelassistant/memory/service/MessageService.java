package com.travelassistant.memory.service;

import com.travelassistant.memory.entity.Conversation;
import com.travelassistant.memory.entity.ConversationMessage;
import com.travelassistant.memory.repository.ConversationMessageRepository;
import com.travelassistant.memory.repository.ConversationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

/**
 * 消息服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class MessageService {

    private final ConversationMessageRepository messageRepository;
    private final ConversationRepository conversationRepository;

    /**
     * 保存消息
     */
    @Transactional
    public String saveMessage(Long userId, String sessionId, String role, String content, 
                          String messageType, java.util.Map<String, Object> metadata) {
        Conversation conversation = conversationRepository.findByUserIdAndSessionId(userId, sessionId)
                .orElseThrow(() -> new RuntimeException("Conversation not found"));
        
        ConversationMessage message = new ConversationMessage();
        message.setConversationId(conversation.getId());
        message.setUserId(userId);
        message.setRole(role);
        message.setContent(content);
        message.setMessageType(messageType != null ? messageType : "text");
        message.setMetadata(metadata != null ? metadata : new java.util.HashMap<>());
        
        ConversationMessage saved = messageRepository.save(message);
        log.info("Saved message: {} for session: {}", saved.getId(), sessionId);
        
        return saved.getId().toString();
    }

    /**
     * 获取消息列表
     */
    public MessageList getMessages(Long userId, String sessionId, Integer limit, Integer offset) {
        Conversation conversation = conversationRepository.findByUserIdAndSessionId(userId, sessionId)
                .orElseThrow(() -> new RuntimeException("Conversation not found"));
        
        List<ConversationMessage> messages = messageRepository.findByConversationIdOrderByCreatedAtDesc(
                conversation.getId()
        ).stream()
                .skip(offset)
                .limit(limit)
                .toList();
        
        long total = messageRepository.countByConversationId(conversation.getId());
        
        return MessageList.builder()
                .messages(messages)
                .total((int) total)
                .build();
    }
}
