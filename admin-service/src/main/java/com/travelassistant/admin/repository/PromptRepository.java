package com.travelassistant.admin.repository;

import com.travelassistant.admin.entity.Prompt;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface PromptRepository extends JpaRepository<Prompt, UUID> {

    Optional<Prompt> findByName(String name);

    List<Prompt> findByCategory(String category);

    Page<Prompt> findByCategory(String category, Pageable pageable);

    List<Prompt> findByIsActiveTrue();

    boolean existsByName(String name);
}
