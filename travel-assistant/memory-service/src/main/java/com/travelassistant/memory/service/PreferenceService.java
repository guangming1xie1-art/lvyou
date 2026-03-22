package com.travelassistant.memory.service;

import com.travelassistant.memory.entity.UserPreference;
import com.travelassistant.memory.repository.UserPreferenceRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 用户偏好服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PreferenceService {

    private final UserPreferenceRepository preferenceRepository;

    /**
     * 保存偏好
     */
    @Transactional
    public String savePreference(Long userId, String preferenceType, String preferenceValue, 
                             Float confidence, String source, Map<String, Object> metadata) {
        // 检查是否已存在
        preferenceRepository.findByUserIdAndPreferenceType(userId, preferenceType)
                .ifPresent(existing -> {
                    existing.setPreferenceValue(preferenceValue);
                    existing.setConfidence(confidence);
                    existing.setSource(source);
                    if (metadata != null) {
                        existing.setMetadata(metadata);
                    }
                    preferenceRepository.save(existing);
                    log.info("Updated preference: {} for user: {}", preferenceType, userId);
                });
        
        // 如果不存在，创建新的
        UserPreference preference = new UserPreference();
        preference.setUserId(userId);
        preference.setPreferenceType(preferenceType);
        preference.setPreferenceValue(preferenceValue);
        preference.setConfidence(confidence != null ? confidence : 0.5f);
        preference.setSource(source);
        preference.setMetadata(metadata != null ? metadata : new HashMap<>());
        
        UserPreference saved = preferenceRepository.save(preference);
        log.info("Saved preference: {} for user: {}", preferenceType, userId);
        
        return saved.getId().toString();
    }

    /**
     * 获取用户偏好
     */
    public List<UserPreference> getUserPreferences(Long userId, String preferenceType) {
        if (preferenceType != null) {
            return preferenceRepository.findByUserIdAndPreferenceType(userId, preferenceType)
                    .map(List::of)
                    .orElse(List.of());
        }
        
        return preferenceRepository.findByUserId(userId);
    }

    /**
     * 更新偏好
     */
    @Transactional
    public void updatePreference(UUID preferenceId, Long userId, String preferenceValue, Float confidence) {
        UserPreference preference = preferenceRepository.findById(preferenceId)
                .orElseThrow(() -> new RuntimeException("Preference not found"));
        
        if (!preference.getUserId().equals(userId)) {
            throw new RuntimeException("Unauthorized");
        }
        
        preference.setPreferenceValue(preferenceValue);
        if (confidence != null) {
            preference.setConfidence(confidence);
        }
        
        preferenceRepository.save(preference);
        log.info("Updated preference: {}", preferenceId);
    }

    /**
     * 删除偏好
     */
    @Transactional
    public void deletePreference(Long userId, UUID preferenceId) {
        UserPreference preference = preferenceRepository.findById(preferenceId)
                .orElseThrow(() -> new RuntimeException("Preference not found"));
        
        if (!preference.getUserId().equals(userId)) {
            throw new RuntimeException("Unauthorized");
        }
        
        preferenceRepository.delete(preference);
        log.info("Deleted preference: {}", preferenceId);
    }
}
