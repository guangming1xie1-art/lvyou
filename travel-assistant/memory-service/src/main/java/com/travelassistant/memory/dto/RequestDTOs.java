package com.travelassistant.memory.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * 创建会话请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateConversationRequest {
    private Long userId;
    private String sessionId;
    private String title;
    private Map<String, Object> metadata;
}

/**
 * 更新摘要请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UpdateSummaryRequest {
    private Long userId;
    private String summary;
}

/**
 * 归档请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ArchiveRequest {
    private Long userId;
}

/**
 * 保存消息请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SaveMessageRequest {
    private Long userId;
    private String sessionId;
    private String role;
    private String content;
    private String messageType;
    private Map<String, Object> metadata;
}

/**
 * 保存偏好请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SavePreferenceRequest {
    private Long userId;
    private String preferenceType;
    private String preferenceValue;
    private Float confidence;
    private String source;
    private Map<String, Object> metadata;
}

/**
 * 更新偏好请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UpdatePreferenceRequest {
    private Long userId;
    private String preferenceValue;
    private Float confidence;
}

/**
 * 保存任务案例请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SaveTaskCaseRequest {
    private Long userId;
    private String destination;
    private Integer durationDays;
    private String budgetRange;
    private java.util.List<String> preferences;
    private String planSummary;
    private Float satisfaction;
    private String feedback;
}

/**
 * 保存向量记忆请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SaveMemoryRequest {
    private Long userId;
    private String memoryType;
    private String content;
    private String embeddingId;
    private Map<String, Object> metadata;
}

/**
 * 向量记忆搜索请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MemorySearchRequest {
    private Long userId;
    private String query;
    private java.util.List<String> memoryTypes;
    private Integer topK;
    private Map<String, Object> filters;
}

/**
 * 提取偏好请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExtractPreferencesRequest {
    private Long userId;
    private String conversationId;
    private Float confidenceThreshold;
}

/**
 * 重置会话请求
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResetSessionRequest {
    private Long userId;
    private Boolean keepSummary;
}
