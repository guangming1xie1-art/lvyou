package com.travelassistant.user.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Convert;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User extends BaseEntity {
  
  // 账户信息
  @Column(unique = true, nullable = false, length = 255)
  private String email;

  @Column(unique = true, nullable = false, length = 100)
  private String username;

  // 用户偏好
  @Column(name = "preferences_json", columnDefinition = "jsonb", nullable = false)
  @Convert(converter = JsonbConverter.class)
  private Map<String, Object> preferencesJson;

  // 审计字段
  @Column(name = "created_by")
  private UUID createdBy;

  @Column(name = "updated_by")
  private UUID updatedBy;

  // 业务逻辑
  @PrePersist
  protected void onCreate() {
    super.onCreate();
    if (preferencesJson == null) {
      preferencesJson = new HashMap<>();
    }
  }

  @PreUpdate
  protected void onUpdate() {
    super.onUpdate();
  }

  /**
   * 获取用户预算等级
   */
  public String getBudgetLevel() {
    if (preferencesJson == null) {
      return "mid";
    }
    Object value = preferencesJson.get("budget_level");
    return value instanceof String ? (String) value : "mid";
  }

  /**
   * 获取用户旅游风格
   */
  public String getTravelStyle() {
    if (preferencesJson == null) {
      return "relaxed";
    }
    Object value = preferencesJson.get("travel_style");
    return value instanceof String ? (String) value : "relaxed";
  }

  /**
   * 获取用户兴趣列表
   */
  @SuppressWarnings("unchecked")
  public List<String> getInterests() {
    if (preferencesJson == null) {
      return new ArrayList<>();
    }
    Object interests = preferencesJson.get("interests");
    return interests instanceof List ? (List<String>) interests : new ArrayList<>();
  }

  /**
   * 获取用户偏好目的地
   */
  @SuppressWarnings("unchecked")
  public List<String> getPreferredDestinations() {
    if (preferencesJson == null) {
      return new ArrayList<>();
    }
    Object destinations = preferencesJson.get("preferred_destinations");
    return destinations instanceof List ? (List<String>) destinations : new ArrayList<>();
  }
}