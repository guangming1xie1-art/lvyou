package com.travelassistant.hotel.entity;

import com.travelassistant.hotel.converter.JsonbConverter;
import jakarta.persistence.Column;
import jakarta.persistence.Convert;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "hotels")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Hotel extends BaseEntity {
  
  // 酒店信息
  @Column(nullable = false, length = 255)
  private String name;

  @Column(nullable = false, length = 100)
  private String destination;

  @Column(nullable = false, precision = 10, scale = 2)
  private BigDecimal price; // ¥/晚

  @Column(nullable = false, precision = 2, scale = 1)
  private BigDecimal rating; // 0-5 分

  @Column(columnDefinition = "TEXT")
  private String description;

  @Column(columnDefinition = "jsonb", nullable = false)
  @Convert(converter = JsonbConverter.class)
  private List<String> facilities; // ["WiFi", "Pool", "Gym"]

  // 日期字段
  @Column(name = "check_in_date")
  private LocalDate checkInDate;

  @Column(name = "check_out_date")
  private LocalDate checkOutDate;

  // 业务逻辑
  @PrePersist
  protected void onCreate() {
    super.onCreate();
    if (rating == null) {
      rating = BigDecimal.ZERO;
    }
    if (facilities == null) {
      facilities = new ArrayList<>();
    }
  }

  @PreUpdate
  protected void onUpdate() {
    super.onUpdate();
  }
}