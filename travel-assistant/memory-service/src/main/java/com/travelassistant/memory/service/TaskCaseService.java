package com.travelassistant.memory.service;

import com.travelassistant.memory.entity.TaskCase;
import com.travelassistant.memory.repository.TaskCaseRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

/**
 * 任务案例服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TaskCaseService {

    private final TaskCaseRepository taskCaseRepository;

    /**
     * 保存任务案例
     */
    @Transactional
    public String saveTaskCase(Long userId, String destination, Integer durationDays, 
                              String budgetRange, List<String> preferences, 
                              String planSummary, Float satisfaction, String feedback) {
        TaskCase taskCase = new TaskCase();
        taskCase.setUserId(userId);
        taskCase.setDestination(destination);
        taskCase.setDurationDays(durationDays);
        taskCase.setBudgetRange(budgetRange);
        taskCase.setPreferences(preferences);
        taskCase.setPlanSummary(planSummary);
        taskCase.setSatisfaction(satisfaction);
        taskCase.setFeedback(feedback);
        
        TaskCase saved = taskCaseRepository.save(taskCase);
        log.info("Saved task case: {} for user: {}", saved.getId(), userId);
        
        return saved.getId().toString();
    }

    /**
     * 获取用户任务案例
     */
    public List<TaskCase> getUserTaskCases(Long userId, String destination, Integer limit) {
        List<TaskCase> cases = taskCaseRepository.findByUserIdAndDestination(userId, destination);
        
        if (limit != null && cases.size() > limit) {
            return cases.subList(0, limit);
        }
        
        return cases;
    }
}
