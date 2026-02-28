package com.travelassistant.attraction.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
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
  @Column(name = "tags", columnDefinition = "text[]")
  private String[] tags;

  // 辅助方法：List <-> 数组转换
  public List<String> getTags() {
    return tags == null ? new ArrayList<>() : new ArrayList<>(Arrays.asList(tags));
  }

  public void setTags(List<String> tagList) {
    this.tags = tagList == null ? new String[0] : tagList.toArray(new String[0]);
  }

  // 业务方法保持不变
  public boolean hasTag(String tag) {
    return getTags().contains(tag);
  }

  public void addTag(String tag) {
    List<String> list = getTags();
    if (!list.contains(tag)) {
      list.add(tag);
      setTags(list);
    }
  }

  public void removeTag(String tag) {
    List<String> list = getTags();
    list.remove(tag);
    setTags(list);
  }

  // 业务逻辑
  @PreUpdate
  protected void onUpdate() {
    super.onUpdate();
  }
}