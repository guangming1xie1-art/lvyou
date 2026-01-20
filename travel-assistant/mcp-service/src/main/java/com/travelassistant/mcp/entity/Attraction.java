package com.travelassistant.mcp.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "attractions", indexes = {
    @Index(name = "idx_attraction_destination", columnList = "destination"),
    @Index(name = "idx_attraction_rating", columnList = "rating")
})
public class Attraction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String destination;
    private String name;
    private String category;
    
    @Column(columnDefinition = "TEXT")
    private String description;
    
    private Double rating;
    
    @Column(name = "opening_hours")
    private String openingHours;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
