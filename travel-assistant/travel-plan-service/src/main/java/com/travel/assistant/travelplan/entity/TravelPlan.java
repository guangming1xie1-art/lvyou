package com.travel.assistant.travelplan.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.travel.assistant.common.entity.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * 旅游计划实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_travel_plan")
public class TravelPlan extends BaseEntity {

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 旅游请求ID
     */
    private Long travelRequestId;

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
     * 行程天数
     */
    private Integer days;

    /**
     * 总预算
     */
    private BigDecimal totalBudget;

    /**
     * 实际花费
     */
    private BigDecimal actualCost;

    /**
     * 行程概览（JSON格式）
     */
    private String itinerary;

    /**
     * 交通安排
     */
    private String transportation;

    /**
     * 住宿安排
     */
    private String accommodation;

    /**
     * 备注
     */
    private String remarks;

    /**
     * 状态（DRAFT、ACTIVE、COMPLETED、CANCELLED）
     */
    private String status;

    /**
     * AI生成的旅行计划内容
     */
    private String aiGeneratedPlan;
}
