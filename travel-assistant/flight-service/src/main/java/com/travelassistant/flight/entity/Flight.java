package com.travelassistant.flight.entity;

import jakarta.persistence.Column;
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
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "flights")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Flight extends BaseEntity {

  // 航线信息
  @Column(name = "flight_no", nullable = false, length = 10)
  private String flightNo;

  // 航线信息
  @Column(nullable = false, length = 100)
  private String origin;

  @Column(nullable = false, length = 100)
  private String destination;

  // 日期
  @Column(name = "departure_date", nullable = false)
  private LocalDate departureDate;

  @Column(name = "return_date")
  private LocalDate returnDate; // 往返航班时有值

  // 价格和航空公司
  @Column(nullable = false, precision = 10, scale = 2)
  private BigDecimal price;

  @Column(nullable = false, length = 100)
  private String airline;

  // 时长（分钟）
  @Column
  private Integer duration;

  // 业务方法
  public String getDurationFormatted() {
    if (duration == null) {
      return "";
    }
    int hours = duration / 60;
    int minutes = duration % 60;
    return String.format("%dh%dm", hours, minutes);
  }
}