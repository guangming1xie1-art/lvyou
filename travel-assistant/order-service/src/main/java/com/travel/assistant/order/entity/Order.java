package com.travel.assistant.order.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.travel.assistant.common.entity.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 订单实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_order")
public class Order extends BaseEntity {

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 关联的旅行计划ID
     */
    private Long travelPlanId;

    /**
     * 订单编号
     */
    private String orderNo;

    /**
     * 订单类型（FLIGHT、HOTEL、CAR、INSURANCE）
     */
    private String orderType;

    /**
     * 供应商名称
     */
    private String supplierName;

    /**
     * 供应商订单号
     */
    private String supplierOrderNo;

    /**
     * 出发地
     */
    private String departure;

    /**
     * 目的地
     */
    private String destination;

    /**
     * 出发时间
     */
    private LocalDateTime departureTime;

    /**
     * 到达时间
     */
    private LocalDateTime arrivalTime;

    /**
     * 联系人
     */
    private String contactName;

    /**
     * 联系电话
     */
    private String contactPhone;

    /**
     * 订单金额
     */
    private BigDecimal amount;

    /**
     * 支付状态（UNPAID、PAID、REFUNDED）
     */
    private String paymentStatus;

    /**
     * 订单状态（PENDING、CONFIRMED、CANCELLED、COMPLETED）
     */
    private String status;

    /**
     * 取消原因
     */
    private String cancelReason;

    /**
     * 备注
     */
    private String remarks;

    /**
     * 详情信息（JSON格式）
     */
    private String details;
}
