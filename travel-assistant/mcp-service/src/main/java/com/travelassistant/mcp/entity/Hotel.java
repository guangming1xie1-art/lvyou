package com.travelassistant.mcp.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "hotels", indexes = {
    @Index(name = "idx_hotel_destination", columnList = "destination"),
    @Index(name = "idx_hotel_price", columnList = "price"),
    @Index(name = "idx_hotel_rating", columnList = "rating")
})
public class Hotel {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    private String destination;
    private Double price;
    private Double rating;
    
    @Column(columnDefinition = "TEXT")
    private String description;
    
    @Column(columnDefinition = "TEXT")
    private String facilities;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
