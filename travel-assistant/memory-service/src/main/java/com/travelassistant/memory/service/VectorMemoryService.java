package com.travelassistant.memory.service;

import com.travelassistant.memory.entity.VectorMemory;
import com.travelassistant.memory.repository.VectorMemoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * 向量记忆服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class VectorMemoryService {

    private final VectorMemoryRepository vectorMemoryRepository;
    private final UserPreferenceRepository preferenceRepository;
    private final TaskCaseRepository taskCaseRepository;

    /**
     * 保存向量记忆
     */
    @Transactional
    public String saveMemory(Long userId, String memoryType, String content, 
                           String embeddingId, Map<String, Object> metadata) {
        VectorMemory memory = new VectorMemory();
        memory.setUserId(userId);
        memory.setMemoryType(memoryType);
        memory.setContent(content);
        memory.setEmbeddingId(embeddingId);
        memory.setMetadata(metadata != null ? metadata : new HashMap<>());
        
        VectorMemory saved = vectorMemoryRepository.save(memory);
        log.info("Saved vector memory: {} for user: {}", saved.getId(), userId);
        
        return saved.getId().toString();
    }

    /**
     * 检索向量记忆
     */
    public List<MemoryResult> searchMemories(Long userId, String query, 
                                          List<String> memoryTypes, Integer topK, 
                                          Map<String, Object> filters) {
        // 这里简化处理，实际应该调用向量数据库（FAISS/Milvus）
        // 1. 从PostgreSQL获取候选数据
        List<VectorMemory> candidates = vectorMemoryRepository.findByUserId(userId).stream()
                .filter(m -> memoryTypes == null || memoryTypes.contains(m.getMemoryType()))
                .collect(Collectors.toList());
        
        // 2. 应用结构化过滤
        if (filters != null) {
            candidates = candidates.stream()
                    .filter(m -> applyFilters(m, filters))
                    .collect(Collectors.toList());
        }
        
        // 3. 模拟向量检索（实际应该调用FAISS/Milvus）
        // 这里简化为基于关键词的匹配
        List<MemoryResult> results = candidates.stream()
                .limit(topK != null ? topK : 5)
                .map(m -> MemoryResult.builder()
                        .id(m.getId().toString())
                        .memoryType(m.getMemoryType())
                        .content(m.getContent())
                        .score(calculateScore(m, query))
                        .metadata(m.getMetadata())
                        .build())
                .collect(Collectors.toList());
        
        log.info("Searched {} memories, returned {} results", candidates.size(), results.size());
        return results;
    }

    /**
     * 提取偏好
     */
    @Transactional
    public List<ExtractedPreference> extractPreferences(Long userId, String conversationId, 
                                                     Float confidenceThreshold) {
        // 这里简化处理，实际应该：
        // 1. 获取对话历史
        // 2. 调用LLM提取偏好
        // 3. 保存提取的偏好
        
        // 模拟返回一些提取的偏好
        return List.of(
                ExtractedPreference.builder()
                        .type("destination_type")
                        .value("海岛")
                        .confidence(0.8f)
                        .source("implicit")
                        .build()
        );
    }

    /**
     * 应用结构化过滤
     */
    private boolean applyFilters(VectorMemory memory, Map<String, Object> filters) {
        Map<String, Object> metadata = memory.getMetadata();
        
        // 最小置信度过滤
        if (filters.containsKey("min_confidence")) {
            Float minConfidence = ((Number) filters.get("min_confidence")).floatValue();
            Float confidence = metadata != null ? (Float) metadata.get("confidence") : 0f;
            if (confidence < minConfidence) {
                return false;
            }
        }
        
        // 最小满意度过滤
        if (filters.containsKey("min_satisfaction")) {
            Float minSatisfaction = ((Number) filters.get("min_satisfaction")).floatValue();
            Float satisfaction = metadata != null ? (Float) metadata.get("satisfaction") : 0f;
            if (satisfaction < minSatisfaction) {
                return false;
            }
        }
        
        return true;
    }

    /**
     * 计算相似度得分（简化版）
     */
    private Float calculateScore(VectorMemory memory, String query) {
        // 简化处理：基于关键词匹配
        String content = memory.getContent().toLowerCase();
        String queryLower = query.toLowerCase();
        
        int matchCount = 0;
        String[] keywords = queryLower.split("\\s+");
        for (String keyword : keywords) {
            if (content.contains(keyword)) {
                matchCount++;
            }
        }
        
        // 计算得分（0-1）
        return (float) matchCount / keywords.length;
    }
}
