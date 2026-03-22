package com.travelassistant.admin.repository;

import com.travelassistant.admin.entity.RagDocument;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Repository
public interface RagDocumentRepository extends JpaRepository<RagDocument, UUID> {

    @Query("SELECT d FROM RagDocument d WHERE d.syncStatus = 'PENDING' ORDER BY d.createdAt ASC")
    List<RagDocument> findPendingSync();

    @Query("SELECT d FROM RagDocument d WHERE d.syncStatus = :status")
    Page<RagDocument> findBySyncStatus(@Param("status") String status, Pageable pageable);

    @Query("SELECT COUNT(d) FROM RagDocument d WHERE d.syncStatus = :status")
    long countByStatus(@Param("status") String status);

    @Modifying
    @Query("UPDATE RagDocument d SET d.syncStatus = :status, d.syncedAt = :syncedAt WHERE d.id IN :ids")
    void batchUpdateSyncStatus(@Param("ids") List<UUID> ids, @Param("status") String status, @Param("syncedAt") LocalDateTime syncedAt);

    @Modifying
    @Query("UPDATE RagDocument d SET d.syncStatus = :status, d.syncedAt = :syncedAt, d.syncError = :error WHERE d.id = :id")
    void updateSyncStatus(@Param("id") UUID id, @Param("status") String status, @Param("syncedAt") LocalDateTime syncedAt, @Param("error") String error);

    List<RagDocument> findByEntityTypeAndEntityId(String entityType, UUID entityId);

    @Query("SELECT d FROM RagDocument d WHERE d.entityType = :entityType AND d.entityId = :entityId")
    List<RagDocument> findByEntity(@Param("entityType") String entityType, @Param("entityId") UUID entityId);
}
