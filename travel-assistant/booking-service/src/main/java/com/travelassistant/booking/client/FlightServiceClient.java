package com.travelassistant.booking.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@FeignClient(name = "flight-service")
public interface FlightServiceClient {
    
    @GetMapping("/api/flight/{id}")
    ResponseEntity<Object> getFlightById(@PathVariable("id") UUID id);
    
    @GetMapping("/api/flight")
    ResponseEntity<List<Object>> getAllFlights();
    
    @GetMapping("/api/flight/route/{origin}/{destination}")
    ResponseEntity<List<Object>> getFlightsByOriginAndDestination(
        @PathVariable("origin") String origin, 
        @PathVariable("destination") String destination);
    
    @GetMapping("/api/flight/date/{departureDate}")
    ResponseEntity<List<Object>> getFlightsByDepartureDate(@PathVariable("departureDate") LocalDate departureDate);
    
    @GetMapping("/api/flight/airline/{airline}")
    ResponseEntity<List<Object>> getFlightsByAirline(@PathVariable("airline") String airline);
}