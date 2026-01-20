package com.travelassistant.booking.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "bookings")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Booking extends BaseEntity {
  
  @Column(nullable = false)
  private UUID userId;
  
  @Column(nullable = false, length = 50)
  private String bookingType; // HOTEL, FLIGHT, ATTRACTION
  
  @Column(nullable = false)
  private UUID resourceId; // 对应的酒店/航班/景点 ID
  
  @Column(name = "booking_date", nullable = false)
  private LocalDateTime bookingDate;
  
  @Column(nullable = false, length = 20)
  private String status; // PENDING, CONFIRMED, CANCELLED
  
  @Column(precision = 10, scale = 2)
  private BigDecimal totalPrice;
  
  @Column(columnDefinition = "TEXT")
  private String notes;

  // 审计字段
  @Column(name = "created_by")
  private UUID createdBy;

  @Column(name = "updated_by")
  private UUID updatedBy;

  // 业务逻辑
  @PrePersist
  protected void onCreate() {
    super.onCreate();
    if (status == null) {
      status = "PENDING";
    }
  }

  @PreUpdate
  protected void onUpdate() {
    super.onUpdate();
  }
}