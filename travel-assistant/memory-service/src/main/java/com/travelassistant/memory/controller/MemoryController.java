package com.travelassistant.memory.controller;

import com.travelassistant.memory.dto.*;
import com.travelassistant.memory.service.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

/**
 * 记忆系统控制器
 * 
 * 提供记忆系统的所有API接口
 */
@Slf4j
@RestController
@RequestMapping("/api/memory")
@RequiredArgsConstructor
public class MemoryController {

    private final ConversationService conversationService;
    private final MessageService messageService;
    private final PreferenceService preferenceService;
    private final TaskCaseService taskCaseService;
    private final VectorMemoryService vectorMemoryService;

    // ==================== 会话管理 ====================

    /**
     * 创建会话
     */
    @PostMapping("/conversations")
    public ResponseEntity<ConversationResponse> createConversation(
            @RequestBody CreateConversationRequest request) {
        log.info("Creating conversation for user: {}", request.getUserId());
        
        Conversation conversation = conversationService.createConversation(
            request.getUserId(),
            request.getSessionId(),
            request.getTitle(),
            request.getMetadata()
        );
        
        return ResponseEntity.ok(ConversationResponse.from(conversation));
    }

    /**
     * 获取会话详情
     */
    @GetMapping("/conversations/{sessionId}")
    public ResponseEntity<ConversationDetailResponse> getConversation(
            @PathVariable String sessionId,
            @RequestParam Long userId) {
        log.info("Getting conversation: {} for user: {}", sessionId, userId);
        
        ConversationDetail detail = conversationService.getConversationDetail(
            userId, sessionId
        );
        
        return ResponseEntity.ok(ConversationDetailResponse.from(detail));
    }

    /**
     * 获取用户会话列表
     */
    @GetMapping("/conversations/user/{userId}")
    public ResponseEntity<ConversationListResponse> getUserConversations(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "20") Integer limit,
            @RequestParam(required = false) String status) {
        log.info("Getting conversations for user: {}", userId);
        
        List<Conversation> conversations = conversationService.getUserConversations(
            userId, limit, status
        );
        
        return ResponseEntity.ok(ConversationListResponse.from(conversations));
    }

    /**
     * 更新会话摘要
     */
    @PostMapping("/conversations/{sessionId}/summary")
    public ResponseEntity<UpdateSummaryResponse> updateSummary(
            @PathVariable String sessionId,
            @RequestBody UpdateSummaryRequest request) {
        log.info("Updating summary for conversation: {}", sessionId);
        
        conversationService.updateSummary(
            request.getUserId(), sessionId, request.getSummary()
        );
        
        return ResponseEntity.ok(UpdateSummaryResponse.success());
    }

    /**
     * 归档会话
     */
    @PostMapping("/conversations/{sessionId}/archive")
    public ResponseEntity<ArchiveResponse> archiveConversation(
            @PathVariable String sessionId,
            @RequestBody ArchiveRequest request) {
        log.info("Archiving conversation: {}", sessionId);
        
        boolean success = conversationService.archiveConversation(
            request.getUserId(), sessionId
        );
        
        return ResponseEntity.ok(ArchiveResponse.from(success));
    }

    /**
     * 删除会话
     */
    @DeleteMapping("/conversations/{sessionId}")
    public ResponseEntity<DeleteResponse> deleteConversation(
            @PathVariable String sessionId,
            @RequestParam Long userId) {
        log.info("Deleting conversation: {}", sessionId);
        
        conversationService.deleteConversation(userId, sessionId);
        
        return ResponseEntity.ok(DeleteResponse.success());
    }

    // ==================== 消息管理 ====================

    /**
     * 保存消息
     */
    @PostMapping("/messages")
    public ResponseEntity<SaveMessageResponse> saveMessage(
            @RequestBody SaveMessageRequest request) {
        log.info("Saving message for session: {}", request.getSessionId());
        
        String messageId = messageService.saveMessage(
            request.getUserId(),
            request.getSessionId(),
            request.getRole(),
            request.getContent(),
            request.getMessageType(),
            request.getMetadata()
        );
        
        return ResponseEntity.ok(SaveMessageResponse.from(messageId));
    }

    /**
     * 获取消息列表
     */
    @GetMapping("/sessions/{sessionId}/messages")
    public ResponseEntity<MessageListResponse> getMessages(
            @PathVariable String sessionId,
            @RequestParam Long userId,
            @RequestParam(defaultValue = "20") Integer limit,
            @RequestParam(defaultValue = "0") Integer offset) {
        log.info("Getting messages for session: {}", sessionId);
        
        MessageList messageList = messageService.getMessages(
            userId, sessionId, limit, offset
        );
        
        return ResponseEntity.ok(MessageListResponse.from(messageList));
    }

    // ==================== 用户偏好管理 ====================

    /**
     * 保存偏好
     */
    @PostMapping("/preferences")
    public ResponseEntity<SavePreferenceResponse> savePreference(
            @RequestBody SavePreferenceRequest request) {
        log.info("Saving preference for user: {}", request.getUserId());
        
        String preferenceId = preferenceService.savePreference(
            request.getUserId(),
            request.getPreferenceType(),
            request.getPreferenceValue(),
            request.getConfidence(),
            request.getSource(),
            request.getMetadata()
        );
        
        return ResponseEntity.ok(SavePreferenceResponse.from(preferenceId));
    }

    /**
     * 获取用户偏好
     */
    @GetMapping("/preferences")
    public ResponseEntity<PreferenceListResponse> getPreferences(
            @RequestParam Long userId,
            @RequestParam(required = false) String preferenceType) {
        log.info("Getting preferences for user: {}", userId);
        
        List<Preference> preferences = preferenceService.getUserPreferences(
            userId, preferenceType
        );
        
        return ResponseEntity.ok(PreferenceListResponse.from(preferences));
    }

    /**
     * 更新偏好
     */
    @PutMapping("/preferences/{preferenceId}")
    public ResponseEntity<UpdatePreferenceResponse> updatePreference(
            @PathVariable UUID preferenceId,
            @RequestBody UpdatePreferenceRequest request) {
        log.info("Updating preference: {}", preferenceId);
        
        preferenceService.updatePreference(
            preferenceId,
            request.getUserId(),
            request.getPreferenceValue(),
            request.getConfidence()
        );
        
        return ResponseEntity.ok(UpdatePreferenceResponse.success());
    }

    /**
     * 删除偏好
     */
    @DeleteMapping("/preferences/{preferenceId}")
    public ResponseEntity<DeleteResponse> deletePreference(
            @PathVariable UUID preferenceId,
            @RequestParam Long userId) {
        log.info("Deleting preference: {}", preferenceId);
        
        preferenceService.deletePreference(userId, preferenceId);
        
        return ResponseEntity.ok(DeleteResponse.success());
    }

    // ==================== 任务案例管理 ====================

    /**
     * 保存任务案例
     */
    @PostMapping("/task-cases")
    public ResponseEntity<SaveTaskCaseResponse> saveTaskCase(
            @RequestBody SaveTaskCaseRequest request) {
        log.info("Saving task case for user: {}", request.getUserId());
        
        String caseId = taskCaseService.saveTaskCase(
            request.getUserId(),
            request.getDestination(),
            request.getDurationDays(),
            request.getBudgetRange(),
            request.getPreferences(),
            request.getPlanSummary(),
            request.getSatisfaction(),
            request.getFeedback()
        );
        
        return ResponseEntity.ok(SaveTaskCaseResponse.from(caseId));
    }

    /**
     * 获取任务案例
     */
    @GetMapping("/task-cases")
    public ResponseEntity<TaskCaseListResponse> getTaskCases(
            @RequestParam Long userId,
            @RequestParam(required = false) String destination,
            @RequestParam(defaultValue = "10") Integer limit) {
        log.info("Getting task cases for user: {}", userId);
        
        List<TaskCase> taskCases = taskCaseService.getUserTaskCases(
            userId, destination, limit
        );
        
        return ResponseEntity.ok(TaskCaseListResponse.from(taskCases));
    }

    // ==================== 向量记忆管理 ====================

    /**
     * 保存向量记忆
     */
    @PostMapping("/memories")
    public ResponseEntity<SaveMemoryResponse> saveMemory(
            @RequestBody SaveMemoryRequest request) {
        log.info("Saving memory for user: {}", request.getUserId());
        
        String memoryId = vectorMemoryService.saveMemory(
            request.getUserId(),
            request.getMemoryType(),
            request.getContent(),
            request.getEmbeddingId(),
            request.getMetadata()
        );
        
        return ResponseEntity.ok(SaveMemoryResponse.from(memoryId));
    }

    /**
     * 检索向量记忆
     */
    @PostMapping("/memories/search")
    public ResponseEntity<MemorySearchResponse> searchMemories(
            @RequestBody MemorySearchRequest request) {
        log.info("Searching memories for user: {}", request.getUserId());
        
        List<MemoryResult> results = vectorMemoryService.searchMemories(
            request.getUserId(),
            request.getQuery(),
            request.getMemoryTypes(),
            request.getTopK(),
            request.getFilters()
        );
        
        return ResponseEntity.ok(MemorySearchResponse.from(results));
    }

    /**
     * 提取偏好
     */
    @PostMapping("/memories/extract-preferences")
    public ResponseEntity<ExtractPreferencesResponse> extractPreferences(
            @RequestBody ExtractPreferencesRequest request) {
        log.info("Extracting preferences for conversation: {}", 
            request.getConversationId());
        
        List<ExtractedPreference> preferences = 
            vectorMemoryService.extractPreferences(
                request.getUserId(),
                request.getConversationId(),
                request.getConfidenceThreshold()
            );
        
        return ResponseEntity.ok(ExtractPreferencesResponse.from(preferences));
    }

    // ==================== 会话统计 ====================

    /**
     * 获取会话统计
     */
    @GetMapping("/sessions/{sessionId}/stats")
    public ResponseEntity<SessionStatsResponse> getSessionStats(
            @PathVariable String sessionId,
            @RequestParam Long userId) {
        log.info("Getting stats for session: {}", sessionId);
        
        SessionStats stats = conversationService.getSessionStats(userId, sessionId);
        
        return ResponseEntity.ok(SessionStatsResponse.from(stats));
    }

    /**
     * 重置会话
     */
    @PostMapping("/sessions/{sessionId}/reset")
    public ResponseEntity<ResetSessionResponse> resetSession(
            @PathVariable String sessionId,
            @RequestBody ResetSessionRequest request) {
        log.info("Resetting session: {}", sessionId);
        
        String newSessionId = conversationService.resetSession(
            request.getUserId(), sessionId, request.getKeepSummary()
        );
        
        return ResponseEntity.ok(ResetSessionResponse.from(newSessionId));
    }
}
