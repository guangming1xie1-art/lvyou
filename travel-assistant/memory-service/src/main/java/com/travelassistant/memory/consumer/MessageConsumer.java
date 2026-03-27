package com.travelassistant.memory.consumer;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.travelassistant.memory.config.RabbitMQConfig;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class MessageConsumer {

    private static final String MESSAGE_BUFFER_PREFIX = "message_buffer:";
    private static final int MAX_BUFFER_SIZE = 100;
    private static final Duration BUFFER_TTL = Duration.ofHours(24);

    private final RedisTemplate<String, Object> redisTemplate;
    private final ObjectMapper objectMapper;

    @RabbitListener(queues = RabbitMQConfig.MESSAGE_QUEUE)
    public void handleMessage(Map<String, Object> messageData) {
        try {
            String sessionId = (String) messageData.get("session_id");
            if (sessionId == null) {
                log.warn("Received message without session_id, skipping");
                return;
            }

            String key = MESSAGE_BUFFER_PREFIX + sessionId;
            
            redisTemplate.opsForList().rightPush(key, messageData);
            
            Long size = redisTemplate.opsForList().size(key);
            if (size != null && size == 1) {
                redisTemplate.expire(key, BUFFER_TTL);
            }
            
            log.debug("Message added to buffer for session: {}, buffer size: {}", sessionId, size);

        } catch (Exception e) {
            log.error("Failed to process message: {}", e.getMessage(), e);
        }
    }
}
