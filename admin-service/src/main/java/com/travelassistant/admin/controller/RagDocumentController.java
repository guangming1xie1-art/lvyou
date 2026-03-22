package com.travelassistant.admin.controller;

import com.travelassistant.admin.dto.RagDTOs;
import com.travelassistant.admin.entity.RagDocument;
import com.travelassistant.admin.service.RagDocumentService;
import com.travelassistant.admin.service.RagSyncService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/admin/rag")
@RequiredArgsConstructor
@Slf4j
public class RagDocumentController {

    private final RagSyncService ragSyncService;
    private final RagDocumentService ragDocumentService;

    // ==================== 同步相关接口 ====================

    @PostMapping("/sync")
    public ResponseEntity<Void> triggerSync() {
        ragSyncService.syncPendingDocuments();
        return ResponseEntity.ok().build();
    }

    @PostMapping("/sync/manual/{documentId}")
    public ResponseEntity<Void> manualSync(@PathVariable UUID documentId) {
        ragSyncService.manualSync(documentId);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/sync/retry-failed")
    public ResponseEntity<Void> retryFailed() {
        ragSyncService.retryFailed();
        return ResponseEntity.ok().build();
    }

    @GetMapping("/sync/status")
    public ResponseEntity<RagDTOs.RagSyncStatusResponse> getSyncStatus() {
        long pending = ragDocumentService.countByStatus("PENDING");
        long synced = ragDocumentService.countByStatus("SYNCED");
        long failed = ragDocumentService.countByStatus("FAILED");

        RagDTOs.RagSyncStatusResponse response = RagDTOs.RagSyncStatusResponse.builder()
                .pendingCount(pending)
                .syncedCount(synced)
                .failedCount(failed)
                .build();

        return ResponseEntity.ok(response);
    }

    // ==================== 文档CRUD接口 ====================

    @GetMapping("/documents")
    public ResponseEntity<Page<RagDocument>> getDocuments(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String entityType) {
        Pageable pageable = PageRequest.of(page, size);
        Page<RagDocument> documents;
        
        if (status != null && !status.isEmpty()) {
            documents = ragDocumentService.findByStatus(status, pageable);
        } else {
            documents = ragDocumentService.findAll(pageable);
        }
        
        return ResponseEntity.ok(documents);
    }

    @GetMapping("/documents/{id}")
    public ResponseEntity<RagDocument> getDocument(@PathVariable UUID id) {
        RagDocument document = ragDocumentService.findById(id);
        return ResponseEntity.ok(document);
    }

    @PostMapping("/documents")
    public ResponseEntity<RagDocument> createDocument(@RequestBody RagDTOs.RagDocumentRequest request) {
        RagDocument document = RagDocument.builder()
                .entityType(request.getEntityType())
                .entityId(request.getEntityId())
                .content(request.getContent())
                .source(request.getSource())
                .metadata(request.getMetadata())
                .docType(request.getDocType())
                .build();
        
        RagDocument saved = ragDocumentService.createDocument(document);
        return ResponseEntity.ok(saved);
    }

    @PutMapping("/documents/{id}")
    public ResponseEntity<RagDocument> updateDocument(
            @PathVariable UUID id,
            @RequestBody RagDTOs.RagDocumentRequest request) {
        RagDocument document = RagDocument.builder()
                .content(request.getContent())
                .source(request.getSource())
                .metadata(request.getMetadata())
                .docType(request.getDocType())
                .build();
        
        RagDocument updated = ragDocumentService.updateDocument(id, document);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/documents/{id}")
    public ResponseEntity<Void> deleteDocument(@PathVariable UUID id) {
        ragDocumentService.deleteDocument(id);
        return ResponseEntity.ok().build();
    }

    // ==================== 切割预览接口 ====================

    @PostMapping("/split/preview")
    public ResponseEntity<RagDTOs.SplitPreviewResponse> previewSplit(@RequestBody RagDTOs.SplitPreviewRequest request) {
        RagDTOs.SplitPreviewResponse response = ragSyncService.previewSplit(request);
        return ResponseEntity.ok(response);
    }
}
