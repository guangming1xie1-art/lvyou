package com.travelassistant.hotel.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Schema(description = "酒店搜索条件")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class HotelSearchCriteria {

    @Schema(description = "目的地")
    private String destination;

    @Schema(description = "最低价格")
    private BigDecimal minPrice;

    @Schema(description = "最高价格")
    private BigDecimal maxPrice;

    @Schema(description = "最低评分")
    private BigDecimal minRating;

    @Schema(description = "最高评分")
    private BigDecimal maxRating;

    @Schema(description = "设施列表（满足任一即可）")
    private List<String> facilities;

    @Schema(description = "入住日期")
    private LocalDate checkInDate;

    @Schema(description = "退住日期")
    private LocalDate checkOutDate;

    @Schema(description = "酒店名称（模糊匹配）")
    private String name;

    @Schema(description = "描述关键词（模糊匹配）")
    private String description;

    @Schema(description = "排序字段: name, price, rating, createdAt")
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
