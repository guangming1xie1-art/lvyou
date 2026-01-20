package com.travelassistant.mcp.dto;

import lombok.Data;

@Data
public class SearchHotelRequest {
    private String destination;
    private Double priceMin = 0.0;
    private Double priceMax = Double.MAX_VALUE;
    private Double ratingMin = 0.0;
}
