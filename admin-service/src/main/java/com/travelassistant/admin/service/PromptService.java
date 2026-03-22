package com.travelassistant.admin.service;

import com.travelassistant.admin.dto.PromptDTOs;
import com.travelassistant.admin.entity.Prompt;
import com.travelassistant.admin.repository.PromptRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class PromptService {

    private final PromptRepository promptRepository;

    public Page<PromptDTOs.PromptResponse> getPrompts(String category, Pageable pageable) {
        if (category != null && !category.isEmpty()) {
            return promptRepository.findByCategory(category, pageable)
                    .map(this::convertToPromptResponse);
        }
        return promptRepository.findAll(pageable)
                .map(this::convertToPromptResponse);
    }

    public List<PromptDTOs.PromptResponse> getActivePrompts() {
        return promptRepository.findByIsActiveTrue().stream()
                .map(this::convertToPromptResponse)
                .collect(Collectors.toList());
    }

    public PromptDTOs.PromptResponse getPrompt(UUID id) {
        Prompt prompt = promptRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Prompt not found: " + id));
        return convertToPromptResponse(prompt);
    }

    @Transactional
    public PromptDTOs.PromptResponse createPrompt(PromptDTOs.PromptRequest request) {
        if (promptRepository.existsByName(request.getName())) {
            throw new RuntimeException("Prompt name already exists");
        }

        Map<String, Object> variablesMap = new HashMap<>();
        if (request.getVariables() != null) {
            variablesMap.put("variables", request.getVariables());
        }

        Prompt prompt = Prompt.builder()
                .name(request.getName())
                .category(request.getCategory())
                .content(request.getContent())
                .variables(variablesMap)
                .description(request.getDescription())
                .version(request.getVersion() != null ? request.getVersion() : "1.0.0")
                .isActive(request.getIsActive() != null ? request.getIsActive() : true)
                .build();

        Prompt saved = promptRepository.save(prompt);
        return convertToPromptResponse(saved);
    }

    @Transactional
    public PromptDTOs.PromptResponse updatePrompt(UUID id, PromptDTOs.PromptRequest request) {
        Prompt prompt = promptRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Prompt not found: " + id));

        prompt.setCategory(request.getCategory());
        prompt.setContent(request.getContent());
        prompt.setDescription(request.getDescription());
        if (request.getVersion() != null) {
            prompt.setVersion(request.getVersion());
        }
        if (request.getIsActive() != null) {
            prompt.setIsActive(request.getIsActive());
        }

        if (request.getVariables() != null) {
            Map<String, Object> variablesMap = new HashMap<>();
            variablesMap.put("variables", request.getVariables());
            prompt.setVariables(variablesMap);
        }

        Prompt updated = promptRepository.save(prompt);
        return convertToPromptResponse(updated);
    }

    @Transactional
    public void deletePrompt(UUID id) {
        promptRepository.deleteById(id);
    }

    public PromptDTOs.PromptTestResponse testPrompt(UUID id, PromptDTOs.PromptTestRequest request) {
        Prompt prompt = promptRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Prompt not found: " + id));

        String renderedPrompt = prompt.getContent();
        if (request.getVariables() != null) {
            for (Map.Entry<String, Object> entry : request.getVariables().entrySet()) {
                renderedPrompt = renderedPrompt.replace(
                        "{{" + entry.getKey() + "}}",
                        String.valueOf(entry.getValue())
                );
            }
        }

        return PromptDTOs.PromptTestResponse.builder()
                .renderedPrompt(renderedPrompt)
                .result("Prompt rendered successfully")
                .build();
    }

    private PromptDTOs.PromptResponse convertToPromptResponse(Prompt prompt) {
        List<String> variables = List.of();
        if (prompt.getVariables() != null && prompt.getVariables().containsKey("variables")) {
            Object vars = prompt.getVariables().get("variables");
            if (vars instanceof List) {
                variables = ((List<?>) vars).stream()
                        .map(Object::toString)
                        .collect(Collectors.toList());
            }
        }

        return PromptDTOs.PromptResponse.builder()
                .id(prompt.getId())
                .name(prompt.getName())
                .category(prompt.getCategory())
                .content(prompt.getContent())
                .variables(variables)
                .description(prompt.getDescription())
                .version(prompt.getVersion())
                .isActive(prompt.getIsActive())
                .createdAt(prompt.getCreatedAt())
                .updatedAt(prompt.getUpdatedAt())
                .build();
    }
}
