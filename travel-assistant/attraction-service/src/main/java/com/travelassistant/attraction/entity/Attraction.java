package com.travelassistant.attraction.entity;

import com.travelassistant.attraction.converter.JsonbConverter;
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
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "attractions")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Attraction extends BaseEntity {
  
  // 基本信息
  @Column(nullable = false, length = 100)
  private String destination;

  @Column(nullable = false, length = 255)
  private String name;

  @Column(length = 50)
  private String category; // "Museum", "Park", "Historic", "Food", "Beach"

  @Column(columnDefinition = "TEXT")
  private String description;

  @Column(nullable = false, precision = 2, scale = 1)
  private BigDecimal rating; // 0-5 分

  @Column(name = "opening_hours", length = 100)
  private String openingHours; // "09:00-18:00"

  // ⭐【核心字段】标签数组，用于搜索和推荐
  @Column(columnDefinition = "jsonb", nullable = false)
  @Convert(converter = JsonbConverter.class)
  private List<String> tags; // ["summer", "beach", "family"] 或 ["winter", "skiing"]

  // 业务逻辑
  @PrePersist
  protected void onCreate() {
    super.onCreate();
    if (rating == null) {
      rating = BigDecimal.ZERO;
    }
    if (tags == null) {
      tags = new ArrayList<>();
    }
  }

  @PreUpdate
  protected void onUpdate() {
    super.onUpdate();
  }

  /**
   * 检查景点是否包含某个标签
   */
  public boolean hasTag(String tag) {
    return tags != null && tags.contains(tag);
  }

  /**
   * 添加标签
   */
  public void addTag(String tag) {
    if (tags == null) {
      tags = new ArrayList<>();
    }
    if (!tags.contains(tag)) {
      tags.add(tag);
    }
  }

  /**
   * 移除标签
   */
  public void removeTag(String tag) {
    if (tags != null) {
      tags.remove(tag);
    }
  }

  /**
   * 获取所有标签（用于搜索）
   */
  public String getTagsAsString() {
    return tags != null ? String.join(",", tags) : "";
  }
}