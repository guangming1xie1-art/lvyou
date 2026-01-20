package com.travelassistant.mcp.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "flights", indexes = {
    @Index(name = "idx_flight_origin", columnList = "origin"),
    @Index(name = "idx_flight_destination", columnList = "destination")
})
public class Flight {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String origin;
    private String destination;
    
    @Column(name = "departure_date")
    private LocalDateTime departureDate;
    
    @Column(name = "return_date")
    private LocalDateTime returnDate;
    
    private Double price;
    private String airline;
    private String duration;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
