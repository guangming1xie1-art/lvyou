package com.travelassistant.memory.dto;

import com.travelassistant.memory.entity.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 会话响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConversationResponse {
    private String conversationId;
    private String sessionId;
    private LocalDateTime createdAt;

    public static ConversationResponse from(Conversation conversation) {
        return ConversationResponse.builder()
                .conversationId(conversation.getId().toString())
                .sessionId(conversation.getSessionId())
                .createdAt(conversation.getCreatedAt())
                .build();
    }
}

/**
 * 会话详情响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConversationDetailResponse {
    private String id;
    private Long userId;
    private String sessionId;
    private String title;
    private String status;
    private String summary;
    private Map<String, Object> metadata;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Integer messageCount;

    public static ConversationDetailResponse from(ConversationDetail detail) {
        Conversation c = detail.getConversation();
        return ConversationDetailResponse.builder()
                .id(c.getId().toString())
                .userId(c.getUserId())
                .sessionId(c.getSessionId())
                .title(c.getTitle())
                .status(c.getStatus())
                .summary(c.getSummary())
                .metadata(c.getMetadata())
                .createdAt(c.getCreatedAt())
                .updatedAt(c.getUpdatedAt())
                .messageCount(detail.getMessageCount())
                .build();
    }
}

/**
 * 会话列表响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConversationListResponse {
    private Integer total;
    private List<ConversationItem> conversations;

    public static ConversationListResponse from(List<Conversation> conversations) {
        List<ConversationItem> items = conversations.stream()
                .map(ConversationItem::from)
                .toList();
        
        return ConversationListResponse.builder()
                .total(items.size())
                .conversations(items)
                .build();
    }
}

/**
 * 会话项
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public static class ConversationItem {
    private String id;
    private String sessionId;
    private String title;
    private String status;
    private LocalDateTime updatedAt;

    public static ConversationItem from(Conversation conversation) {
        return ConversationItem.builder()
                .id(conversation.getId().toString())
                .sessionId(conversation.getSessionId())
                .title(conversation.getTitle())
                .status(conversation.getStatus())
                .updatedAt(conversation.getUpdatedAt())
                .build();
    }
}

/**
 * 更新摘要响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public static class UpdateSummaryResponse {
    private Boolean success;
    private LocalDateTime updatedAt;

    public static UpdateSummaryResponse success() {
        return UpdateSummaryResponse.builder()
                .success(true)
                .updatedAt(LocalDateTime.now())
                .build();
    }
}

/**
 * 归档响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public static class ArchiveResponse {
    private Boolean success;
    private LocalDateTime archivedAt;

    public static ArchiveResponse from(boolean success) {
        return ArchiveResponse.builder()
                .success(success)
                .archivedAt(LocalDateTime.now())
                .build();
    }
}

/**
 * 删除响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public static class DeleteResponse {
    private Boolean success;
    private LocalDateTime deletedAt;

    public static DeleteResponse success() {
        return DeleteResponse.builder()
                .success(true)
                .deletedAt(LocalDateTime.now())
                .build();
    }
}

/**
 * 保存消息响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SaveMessageResponse {
    private Boolean success;
    private String messageId;
    private LocalDateTime createdAt;

    public static SaveMessageResponse from(String messageId) {
        return SaveMessageResponse.builder()
                .success(true)
                .messageId(messageId)
                .createdAt(LocalDateTime.now())
                .build();
    }
}

/**
 * 消息列表响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MessageListResponse {
    private Integer total;
    private List<MessageItem> messages;

    public static MessageListResponse from(MessageList messageList) {
        List<MessageItem> items = messageList.getMessages().stream()
                .map(MessageItem::from)
                .toList();
        
        return MessageListResponse.builder()
                .total(messageList.getTotal())
                .messages(items)
                .build();
    }
}

/**
 * 消息项
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public static class MessageItem {
    private String id;
    private String conversationId;
    private Long userId;
    private String role;
    private String content;
    private String messageType;
    private Map<String, Object> metadata;
    private LocalDateTime createdAt;

    public static MessageItem from(ConversationMessage message) {
        return MessageItem.builder()
                .id(message.getId().toString())
                .conversationId(message.getConversationId().toString())
                .userId(message.getUserId())
                .role(message.getRole())
                .content(message.getContent())
                .messageType(message.getMessageType())
                .metadata(message.getMetadata())
                .createdAt(message.getCreatedAt())
                .build();
    }
}

/**
 * 保存偏好响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SavePreferenceResponse {
    private Boolean success;
    private String preferenceId;
    private LocalDateTime createdAt;

    public static SavePreferenceResponse from(String preferenceId) {
        return SavePreferenceResponse.builder()
                .success(true)
                .preferenceId(preferenceId)
                .createdAt(LocalDateTime.now())
                .build();
    }
}

/**
 * 更新偏好响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public static class UpdatePreferenceResponse {
    private Boolean success;
    private LocalDateTime updatedAt;

    public static UpdatePreferenceResponse success() {
        return UpdatePreferenceResponse.builder()
                .success(true)
                .updatedAt(LocalDateTime.now())
                .build();
    }
}

/**
 * 偏好列表响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PreferenceListResponse {
    private Integer total;
    private List<PreferenceItem> preferences;

    public static PreferenceListResponse from(List<UserPreference> preferences) {
        List<PreferenceItem> items = preferences.stream()
                .map(PreferenceItem::from)
                .toList();
        
        return PreferenceListResponse.builder()
                .total(items.size())
                .preferences(items)
                .build();
    }
}

/**
 * 偏好项
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public static class PreferenceItem {
    private String id;
    private Long userId;
    private String preferenceType;
    private String preferenceValue;
    private Float confidence;
    private String source;
    private Map<String, Object> metadata;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public static PreferenceItem from(UserPreference preference) {
        return PreferenceItem.builder()
                .id(preference.getId().toString())
                .userId(preference.getUserId())
                .preferenceType(preference.getPreferenceType())
                .preferenceValue(preference.getPreferenceValue())
                .confidence(preference.getConfidence())
                .source(preference.getSource())
                .metadata(preference.getMetadata())
                .createdAt(preference.getCreatedAt())
                .updatedAt(preference.getUpdatedAt())
                .build();
    }
}

/**
 * 保存任务案例响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SaveTaskCaseResponse {
    private Boolean success;
    private String caseId;
    private LocalDateTime createdAt;

    public static SaveTaskCaseResponse from(String caseId) {
        return SaveTaskCaseResponse.builder()
                .success(true)
                .caseId(caseId)
                .createdAt(LocalDateTime.now())
                .build();
    }
}

/**
 * 任务案例列表响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TaskCaseListResponse {
    private Integer total;
    private List<TaskCaseItem> cases;

    public static TaskCaseListResponse from(List<TaskCase> taskCases) {
        List<TaskCaseItem> items = taskCases.stream()
                .map(TaskCaseItem::from)
                .toList();
        
        return TaskCaseListResponse.builder()
                .total(items.size())
                .cases(items)
                .build();
    }
}

/**
 * 任务案例项
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public static class TaskCaseItem {
    private String id;
    private Long userId;
    private String destination;
    private Integer durationDays;
    private String budgetRange;
    private List<String> preferences;
    private String planSummary;
    private Float satisfaction;
    private String feedback;
    private LocalDateTime createdAt;

    public static TaskCaseItem from(TaskCase taskCase) {
        return TaskCaseItem.builder()
                .id(taskCase.getId().toString())
                .userId(taskCase.getUserId())
                .destination(taskCase.getDestination())
                .durationDays(taskCase.getDurationDays())
                .budgetRange(taskCase.getBudgetRange())
                .preferences(taskCase.getPreferences())
                .planSummary(taskCase.getPlanSummary())
                .satisfaction(taskCase.getSatisfaction())
                .feedback(taskCase.getFeedback())
                .createdAt(taskCase.getCreatedAt())
                .build();
    }
}

/**
 * 保存向量记忆响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SaveMemoryResponse {
    private Boolean success;
    private String memoryId;
    private LocalDateTime createdAt;

    public static SaveMemoryResponse from(String memoryId) {
        return SaveMemoryResponse.builder()
                .success(true)
                .memoryId(memoryId)
                .createdAt(LocalDateTime.now())
                .build();
    }
}

/**
 * 向量记忆搜索结果
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MemoryResult {
    private String id;
    private String memoryType;
    private String content;
    private Float score;
    private Map<String, Object> metadata;
}

/**
 * 向量记忆搜索响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MemorySearchResponse {
    private Integer total;
    private List<MemoryResult> memories;

    public static MemorySearchResponse from(List<MemoryResult> results) {
        return MemorySearchResponse.builder()
                .total(results.size())
                .memories(results)
                .build();
    }
}

/**
 * 提取的偏好
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExtractedPreference {
    private String type;
    private String value;
    private Float confidence;
    private String source;
}

/**
 * 提取偏好响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExtractPreferencesResponse {
    private Integer total;
    private List<ExtractedPreference> preferences;

    public static ExtractPreferencesResponse from(List<ExtractedPreference> preferences) {
        return ExtractPreferencesResponse.builder()
                .total(preferences.size())
                .preferences(preferences)
                .build();
    }
}

/**
 * 会话统计响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionStatsResponse {
    private String sessionId;
    private Integer messageCount;
    private Long totalTokens;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Boolean needsReset;
    private String resetReason;

    public static SessionStatsResponse from(SessionStats stats) {
        return SessionStatsResponse.builder()
                .sessionId(stats.getSessionId())
                .messageCount(stats.getMessageCount())
                .totalTokens(stats.getTotalTokens())
                .createdAt(stats.getCreatedAt())
                .updatedAt(stats.getUpdatedAt())
                .needsReset(stats.getNeedsReset())
                .resetReason(stats.getResetReason())
                .build();
    }
}

/**
 * 重置会话响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResetSessionResponse {
    private Boolean success;
    private String newSessionId;
    private LocalDateTime resetAt;

    public static ResetSessionResponse from(String newSessionId) {
        return ResetSessionResponse.builder()
                .success(true)
                .newSessionId(newSessionId)
                .resetAt(LocalDateTime.now())
                .build();
    }
}
