package com.travelassistant.admin.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

public class DashboardDTOs {

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class DashboardStatsResponse {
        private Long userCount;
        private Long documentCount;
        private Long syncedCount;
        private Long pendingCount;
        private Long failedCount;
        private Long todayActiveUsers;
        private Long todayApiCalls;
        private List<ServiceStatus> services;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class ServiceStatus {
        private String name;
        private String status;
        private Integer instances;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class SyncStatusResponse {
        private Long pendingCount;
        private Long syncedCount;
        private Long failedCount;
        private String lastSyncTime;
    }
}
