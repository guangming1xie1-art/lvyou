package com.travelassistant.mcp.dto;

import lombok.Data;

@Data
public class RecommendRequest {
    private String email;
    private String destination;
}
