package com.travelassistant.memory.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 历史任务案例实体
 */
@Data
@Entity
@Table(name = "task_cases")
public class TaskCase {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id")
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "destination", length = 255)
    private String destination;

    @Column(name = "duration_days")
    private Integer durationDays;

    @Column(name = "budget_range", length = 50)
    private String budgetRange;

    @Column(name = "preferences", columnDefinition = "jsonb")
    private List<String> preferences;

    @Column(name = "plan_summary", columnDefinition = "TEXT")
    private String planSummary;

    @Column(name = "satisfaction")
    private Float satisfaction;

    @Column(name = "feedback", columnDefinition = "TEXT")
    private String feedback;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
