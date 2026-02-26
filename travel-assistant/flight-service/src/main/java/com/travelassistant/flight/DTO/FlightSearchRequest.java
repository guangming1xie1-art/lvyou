package com.travelassistant.flight.DTO;

import lombok.Data;

import java.time.LocalDate;

@Data
public class FlightSearchRequest {
    private String origin;
    private String destination;
    private LocalDate departureDate;
    private Double minPrice;
    private Double maxPrice;
    private String airline;
}
