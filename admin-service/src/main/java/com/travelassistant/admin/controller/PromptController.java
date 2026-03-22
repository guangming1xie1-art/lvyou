package com.travelassistant.admin.controller;

import com.travelassistant.admin.dto.PromptDTOs;
import com.travelassistant.admin.service.PromptService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/admin/prompts")
@RequiredArgsConstructor
@Slf4j
public class PromptController {

    private final PromptService promptService;

    @GetMapping
    public ResponseEntity<Page<PromptDTOs.PromptResponse>> getPrompts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String category) {
        Pageable pageable = PageRequest.of(page, size);
        return ResponseEntity.ok(promptService.getPrompts(category, pageable));
    }

    @GetMapping("/active")
    public ResponseEntity<List<PromptDTOs.PromptResponse>> getActivePrompts() {
        return ResponseEntity.ok(promptService.getActivePrompts());
    }

    @GetMapping("/{id}")
    public ResponseEntity<PromptDTOs.PromptResponse> getPrompt(@PathVariable UUID id) {
        return ResponseEntity.ok(promptService.getPrompt(id));
    }

    @PostMapping
    public ResponseEntity<PromptDTOs.PromptResponse> createPrompt(@RequestBody PromptDTOs.PromptRequest request) {
        return ResponseEntity.ok(promptService.createPrompt(request));
    }

    @PutMapping("/{id}")
    public ResponseEntity<PromptDTOs.PromptResponse> updatePrompt(
            @PathVariable UUID id,
            @RequestBody PromptDTOs.PromptRequest request) {
        return ResponseEntity.ok(promptService.updatePrompt(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePrompt(@PathVariable UUID id) {
        promptService.deletePrompt(id);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/{id}/test")
    public ResponseEntity<PromptDTOs.PromptTestResponse> testPrompt(
            @PathVariable UUID id,
            @RequestBody PromptDTOs.PromptTestRequest request) {
        return ResponseEntity.ok(promptService.testPrompt(id, request));
    }
}
