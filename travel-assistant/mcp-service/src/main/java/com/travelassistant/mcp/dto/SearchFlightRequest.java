package com.travelassistant.mcp.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class SearchFlightRequest {
    private String origin;
    private String destination;
    private LocalDateTime departureDate;
    private LocalDateTime returnDate;
}
