package com.travelassistant.admin.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class PromptDTOs {

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class PromptRequest {
        private String name;
        private String category;
        private String content;
        private List<String> variables;
        private String description;
        private String version;
        private Boolean isActive;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class PromptResponse {
        private UUID id;
        private String name;
        private String category;
        private String content;
        private List<String> variables;
        private String description;
        private String version;
        private Boolean isActive;
        private LocalDateTime createdAt;
        private LocalDateTime updatedAt;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class PromptTestRequest {
        private Map<String, Object> variables;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class PromptTestResponse {
        private String renderedPrompt;
        private String result;
    }
}
