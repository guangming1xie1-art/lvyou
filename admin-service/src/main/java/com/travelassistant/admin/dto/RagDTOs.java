package com.travelassistant.admin.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;
import java.util.UUID;

public class RagDTOs {

    // ==================== 文档处理请求/响应 ====================

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class DocumentItem {
        private String content;
        private Map<String, Object> metadata;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class DocumentProcessRequest {
        private List<DocumentItem> documents;
        private Boolean autoSplit = true;
        private Integer chunkSize = 500;
        private Integer chunkOverlap = 50;
        private String docType = "default";
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class DocumentProcessResponse {
        private String status;
        private Integer originalCount;
        private Integer chunkCount;
        private StrategyInfo strategy;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class StrategyInfo {
        private Boolean autoSplit;
        private Integer chunkSize;
        private Integer chunkOverlap;
    }

    // ==================== 切割预览请求/响应 ====================

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class SplitPreviewRequest {
        private List<DocumentItem> documents;
        private Integer chunkSize = 500;
        private Integer chunkOverlap = 50;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class SplitPreviewResponse {
        private String status;
        private List<ChunkItem> chunks;
        private Integer chunkCount;
        private Integer originalCount;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class ChunkItem {
        private String content;
        private Map<String, Object> metadata;
    }

    // ==================== 同步状态响应 ====================

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class RagSyncStatusResponse {
        private Long pendingCount;
        private Long syncedCount;
        private Long failedCount;
    }

    // ==================== RAG文档请求 ====================

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class RagDocumentRequest {
        private String entityType;
        private UUID entityId;
        private String content;
        private String source;
        private String docType;
        private Map<String, Object> metadata;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class RagSyncRequest {
        private List<UUID> documentIds;
        private Boolean autoSplit = true;
        private Integer chunkSize = 500;
        private Integer chunkOverlap = 50;
    }
}
