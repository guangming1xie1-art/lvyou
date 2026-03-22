package com.travelassistant.memory.dto;

import com.travelassistant.memory.entity.Conversation;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 会话详情（内部使用）
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConversationDetail {
    private Conversation conversation;
    private Integer messageCount;
}

/**
 * 消息列表（内部使用）
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MessageList {
    private java.util.List<com.travelassistant.memory.entity.ConversationMessage> messages;
    private Integer total;
}

/**
 * 会话统计（内部使用）
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionStats {
    private String sessionId;
    private Integer messageCount;
    private Long totalTokens;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Boolean needsReset;
    private String resetReason;
}
