package com.travelassistant.attraction.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Schema(description = "景点搜索条件")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AttractionSearchCriteria {

    @Schema(description = "目的地")
    private String destination;

    @Schema(description = "景点名称（模糊匹配）")
    private String name;

    @Schema(description = "类别: Museum, Park, Historic, Food, Beach")
    private String category;

    @Schema(description = "最低评分")
    private BigDecimal minRating;

    @Schema(description = "最高评分")
    private BigDecimal maxRating;

    @Schema(description = "标签列表（满足任一即可）")
    private List<String> tags;

    @Schema(description = "描述关键词（模糊匹配）")
    private String description;

    @Schema(description = "营业时间")
    private String openingHours;

    @Schema(description = "排序字段: name, rating, category, createdAt")
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
