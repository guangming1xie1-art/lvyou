package com.travel.assistant.travelrequest.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.travel.assistant.common.entity.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * 旅游请求实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_travel_request")
public class TravelRequest extends BaseEntity {

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 目的地
     */
    private String destination;

    /**
     * 出发日期
     */
    private LocalDate startDate;

    /**
     * 结束日期
     */
    private LocalDate endDate;

    /**
     * 预算
     */
    private BigDecimal budget;

    /**
     * 人数
     */
    private Integer travelerCount;

    /**
     * 出行方式（AIRPLANE、TRAIN、BUS、CAR）
     */
    private String travelMode;

    /**
     * 住宿偏好
     */
    private String accommodationPreference;

    /**
     * 特殊需求
     */
    private String specialRequirements;

    /**
     * 状态（PENDING、PROCESSING、COMPLETED、CANCELLED）
     */
    private String status;

    /**
     * 优先级（LOW、MEDIUM、HIGH）
     */
    private String priority;
}
