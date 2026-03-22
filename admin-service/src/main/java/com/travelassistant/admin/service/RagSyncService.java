package com.travelassistant.admin.service;

import com.travelassistant.admin.client.AdminAgentClient;
import com.travelassistant.admin.dto.RagDTOs;
import com.travelassistant.admin.entity.RagDocument;
import com.travelassistant.admin.repository.RagDocumentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Pageable;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class RagSyncService {

    private final RagDocumentRepository ragDocumentRepository;
    private final AdminAgentClient adminAgentClient;

    @Value("${rag.sync.batch-size:50}")
    private int batchSize;

    @Value("${rag.sync.enabled:true}")
    private boolean syncEnabled;

    @Scheduled(cron = "${rag.sync.cron:0 0 * * * ?}")
    public void scheduledSync() {
        if (!syncEnabled) {
            log.debug("RAG sync is disabled");
            return;
        }

        log.info("Starting scheduled RAG document sync...");
        syncPendingDocuments();
    }

    public void syncPendingDocuments() {
        List<RagDocument> pendingDocs = ragDocumentRepository.findPendingSync();

        if (pendingDocs.isEmpty()) {
            log.info("No documents to sync");
            return;
        }

        log.info("Found {} documents to sync", pendingDocs.size());

        List<List<RagDocument>> batches = partitionList(pendingDocs, batchSize);

        for (List<RagDocument> batch : batches) {
            processBatch(batch);
        }
    }

    private void processBatch(List<RagDocument> batch) {
        List<RagDTOs.DocumentItem> documents = batch.stream()
                .map(this::buildSyncDocument)
                .collect(Collectors.toList());

        RagDTOs.DocumentProcessRequest request = RagDTOs.DocumentProcessRequest.builder()
                .documents(documents)
                .autoSplit(true)
                .chunkSize(500)
                .chunkOverlap(50)
                .build();

        adminAgentClient.processDocuments(request)
                .subscribe(
                        response -> handleSyncSuccess(batch, response),
                        error -> handleSyncError(batch, error)
                );
    }

    private RagDTOs.DocumentItem buildSyncDocument(RagDocument doc) {
        Map<String, Object> metadata = new HashMap<>();
        if (doc.getMetadata() != null) {
            metadata.putAll(doc.getMetadata());
        }
        metadata.put("entity_type", doc.getEntityType());
        metadata.put("entity_id", doc.getEntityId().toString());
        metadata.put("source", doc.getSource());
        metadata.put("doc_id", doc.getId().toString());

        return RagDTOs.DocumentItem.builder()
                .content(doc.getContent())
                .metadata(metadata)
                .build();
    }

    private void handleSyncSuccess(List<RagDocument> batch, RagDTOs.DocumentProcessResponse response) {
        List<UUID> syncedIds = batch.stream()
                .map(RagDocument::getId)
                .collect(Collectors.toList());

        ragDocumentRepository.batchUpdateSyncStatus(
                syncedIds,
                "SYNCED",
                LocalDateTime.now()
        );

        log.info("Successfully synced {} documents ({} chunks)",
                batch.size(), response.getChunkCount());
    }

    private void handleSyncError(List<RagDocument> batch, Throwable error) {
        log.error("Failed to sync {} documents: {}", batch.size(), error.getMessage());

        for (RagDocument doc : batch) {
            ragDocumentRepository.updateSyncStatus(
                    doc.getId(),
                    "FAILED",
                    LocalDateTime.now(),
                    error.getMessage()
            );
        }
    }

    public void manualSync(UUID documentId) {
        RagDocument doc = ragDocumentRepository.findById(documentId)
                .orElseThrow(() -> new RuntimeException("Document not found: " + documentId));

        processBatch(List.of(doc));
    }

    public void retryFailed() {
        List<RagDocument> failedDocs = ragDocumentRepository.findBySyncStatus("FAILED", Pageable.unpaged())
                .getContent();

        if (failedDocs.isEmpty()) {
            log.info("No failed documents to retry");
            return;
        }

        log.info("Retrying {} failed documents", failedDocs.size());

        List<List<RagDocument>> batches = partitionList(failedDocs, batchSize);
        for (List<RagDocument> batch : batches) {
            processBatch(batch);
        }
    }

    public RagDTOs.SplitPreviewResponse previewSplit(RagDTOs.SplitPreviewRequest request) {
        return adminAgentClient.previewSplit(request).block();
    }

    private <T> List<List<T>> partitionList(List<T> list, int size) {
        return java.util.stream.IntStream.range(0, (list.size() + size - 1) / size)
                .mapToObj(i -> list.subList(i * size, Math.min((i + 1) * size, list.size())))
                .collect(Collectors.toList());
    }
}
