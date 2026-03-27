package com.travelassistant.memory.scheduler;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.travelassistant.memory.entity.Conversation;
import com.travelassistant.memory.entity.ConversationMessage;
import com.travelassistant.memory.repository.ConversationMessageRepository;
import com.travelassistant.memory.repository.ConversationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

@Slf4j
@Component
@RequiredArgsConstructor
public class MessageBatchProcessor {

    private static final String MESSAGE_BUFFER_PREFIX = "message_buffer:";
    private static final int BATCH_SIZE = 100;

    private final RedisTemplate<String, Object> redisTemplate;
    private final ConversationRepository conversationRepository;
    private final ConversationMessageRepository messageRepository;
    private final ObjectMapper objectMapper;

    @Scheduled(fixedRate = 1000)
    @Transactional
    public void processMessageBuffer() {
        Set<String> keys = redisTemplate.keys(MESSAGE_BUFFER_PREFIX + "*");
        if (keys == null || keys.isEmpty()) {
            return;
        }

        for (String key : keys) {
            try {
                processSessionBuffer(key);
            } catch (Exception e) {
                log.error("Failed to process buffer for key: {}", key, e);
            }
        }
    }

    private void processSessionBuffer(String key) {
        Long size = redisTemplate.opsForList().size(key);
        if (size == null || size == 0) {
            return;
        }

        int toProcess = Math.min(size.intValue(), BATCH_SIZE);
        
        List<Object> rawMessages = redisTemplate.opsForList().leftPop(key, toProcess);
        if (rawMessages == null || rawMessages.isEmpty()) {
            return;
        }

        List<Map<String, Object>> messages = convertMessages(rawMessages);
        if (messages.isEmpty()) {
            return;
        }

        String sessionId = key.replace(MESSAGE_BUFFER_PREFIX, "");
        Conversation conversation = getOrCreateConversation(sessionId, messages);
        
        List<ConversationMessage> entities = new ArrayList<>();
        for (Map<String, Object> msg : messages) {
            ConversationMessage entity = convertToEntity(msg, conversation.getId());
            entities.add(entity);
        }

        messageRepository.saveAll(entities);
        log.info("Batch saved {} messages for session: {}", entities.size(), sessionId);
    }

    private Conversation getOrCreateConversation(String sessionId, List<Map<String, Object>> messages) {
        return conversationRepository.findBySessionId(sessionId)
            .orElseGet(() -> {
                Map<String, Object> firstMsg = messages.get(0);
                Long userId = getLongValue(firstMsg, "user_id");
                
                Conversation conv = new Conversation();
                conv.setId(UUID.randomUUID());
                conv.setSessionId(sessionId);
                conv.setUserId(userId);
                conv.setTitle("对话 " + sessionId.substring(0, 8));
                conv.setStatus("active");
                return conversationRepository.save(conv);
            });
    }

    private ConversationMessage convertToEntity(Map<String, Object> msg, UUID conversationId) {
        ConversationMessage entity = new ConversationMessage();
        entity.setId(UUID.randomUUID());
        entity.setConversationId(conversationId);
        entity.setUserId(getLongValue(msg, "user_id"));
        entity.setRole(getStringValue(msg, "role", "user"));
        entity.setContent(getStringValue(msg, "content", ""));
        
        String timestamp = getStringValue(msg, "timestamp", null);
        if (timestamp != null) {
            try {
                entity.setCreatedAt(LocalDateTime.parse(timestamp));
            } catch (Exception e) {
                entity.setCreatedAt(LocalDateTime.now());
            }
        } else {
            entity.setCreatedAt(LocalDateTime.now());
        }

        @SuppressWarnings("unchecked")
        Map<String, Object> metadata = (Map<String, Object>) msg.get("metadata");
        entity.setMetadata(metadata);
        
        return entity;
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> convertMessages(List<Object> rawMessages) {
        List<Map<String, Object>> result = new ArrayList<>();
        for (Object raw : rawMessages) {
            if (raw instanceof Map) {
                result.add((Map<String, Object>) raw);
            }
        }
        return result;
    }

    private Long getLongValue(Map<String, Object> map, String key) {
        Object value = map.get(key);
        if (value == null) return 0L;
        if (value instanceof Number) {
            return ((Number) value).longValue();
        }
        try {
            return Long.parseLong(value.toString());
        } catch (NumberFormatException e) {
            return 0L;
        }
    }

    private String getStringValue(Map<String, Object> map, String key, String defaultValue) {
        Object value = map.get(key);
        return value != null ? value.toString() : defaultValue;
    }
}
