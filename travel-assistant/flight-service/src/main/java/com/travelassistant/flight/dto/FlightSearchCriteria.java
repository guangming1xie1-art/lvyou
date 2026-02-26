package com.travelassistant.flight.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

@Schema(description = "航班搜索条件")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FlightSearchCriteria {

    @Schema(description = "出发地")
    private String origin;

    @Schema(description = "目的地")
    private String destination;

    @Schema(description = "出发日期开始范围")
    private LocalDate departureDateStart;

    @Schema(description = "出发日期结束范围")
    private LocalDate departureDateEnd;

    @Schema(description = "返回日期开始范围")
    private LocalDate returnDateStart;

    @Schema(description = "返回日期结束范围")
    private LocalDate returnDateEnd;

    @Schema(description = "最低价格")
    private BigDecimal minPrice;

    @Schema(description = "最高价格")
    private BigDecimal maxPrice;

    @Schema(description = "航空公司")
    private String airline;

    @Schema(description = "航班号（模糊匹配）")
    private String flightNo;

    @Schema(description = "最短时长（分钟）")
    private Integer minDuration;

    @Schema(description = "最长时长（分钟）")
    private Integer maxDuration;

    @Schema(description = "排序字段: flightNo, origin, destination, departureDate, price, airline, duration, createdAt")
    @Builder.Default
    private String sortBy = "createdAt";

    @Schema(description = "排序方向: asc, desc")
    @Builder.Default
    private String sortDirection = "desc";

    @Schema(description = "页码，从0开始")
    @Builder.Default
    private Integer page = 0;

    @Schema(description = "每页大小")
    @Builder.Default
    private Integer size = 10;
}
