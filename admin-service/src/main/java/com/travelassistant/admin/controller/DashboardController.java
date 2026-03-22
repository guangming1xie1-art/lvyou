package com.travelassistant.admin.controller;

import com.travelassistant.admin.dto.DashboardDTOs;
import com.travelassistant.admin.repository.AdminUserRepository;
import com.travelassistant.admin.repository.RagDocumentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/admin/dashboard")
@RequiredArgsConstructor
@Slf4j
public class DashboardController {

    private final AdminUserRepository adminUserRepository;
    private final RagDocumentRepository ragDocumentRepository;

    @GetMapping("/stats")
    public ResponseEntity<DashboardDTOs.DashboardStatsResponse> getStats() {
        long userCount = adminUserRepository.count();
        long documentCount = ragDocumentRepository.count();
        long syncedCount = ragDocumentRepository.countByStatus("SYNCED");
        long pendingCount = ragDocumentRepository.countByStatus("PENDING");
        long failedCount = ragDocumentRepository.countByStatus("FAILED");

        DashboardDTOs.DashboardStatsResponse response = DashboardDTOs.DashboardStatsResponse.builder()
                .userCount(userCount)
                .documentCount(documentCount)
                .syncedCount(syncedCount)
                .pendingCount(pendingCount)
                .failedCount(failedCount)
                .todayActiveUsers(0L)  // TODO: 实现统计
                .todayApiCalls(0L)     // TODO: 实现统计
                .services(List.of(
                        DashboardDTOs.ServiceStatus.builder()
                                .name("admin-service")
                                .status("UP")
                                .instances(1)
                                .build(),
                        DashboardDTOs.ServiceStatus.builder()
                                .name("admin-agent")
                                .status("UP")
                                .instances(1)
                                .build()
                ))
                .build();

        return ResponseEntity.ok(response);
    }
}
