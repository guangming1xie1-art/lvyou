package com.travelassistant.admin.service;

import com.travelassistant.admin.entity.RagDocument;
import com.travelassistant.admin.repository.RagDocumentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class RagDocumentService {

    private final RagDocumentRepository ragDocumentRepository;

    public long countByStatus(String status) {
        return ragDocumentRepository.countByStatus(status);
    }

    public Page<RagDocument> findByStatus(String status, Pageable pageable) {
        return ragDocumentRepository.findBySyncStatus(status, pageable);
    }

    public Page<RagDocument> findAll(Pageable pageable) {
        return ragDocumentRepository.findAll(pageable);
    }

    public List<RagDocument> findByEntity(String entityType, UUID entityId) {
        return ragDocumentRepository.findByEntity(entityType, entityId);
    }

    @Transactional
    public RagDocument createDocument(RagDocument document) {
        document.setSyncStatus("PENDING");
        return ragDocumentRepository.save(document);
    }

    @Transactional
    public RagDocument updateDocument(UUID id, RagDocument document) {
        RagDocument existing = ragDocumentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Document not found: " + id));

        if (document.getContent() != null) {
            existing.setContent(document.getContent());
        }
        if (document.getDocType() != null) {
            existing.setDocType(document.getDocType());
        }
        if (document.getSource() != null) {
            existing.setSource(document.getSource());
        }
        if (document.getMetadata() != null) {
            existing.setMetadata(document.getMetadata());
        }
        existing.setSyncStatus("PENDING");

        return ragDocumentRepository.save(existing);
    }

    @Transactional
    public void deleteDocument(UUID id) {
        ragDocumentRepository.deleteById(id);
    }

    public RagDocument findById(UUID id) {
        return ragDocumentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Document not found: " + id));
    }
}
