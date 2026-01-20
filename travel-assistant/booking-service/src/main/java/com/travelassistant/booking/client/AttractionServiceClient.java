package com.travelassistant.booking.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@FeignClient(name = "attraction-service")
public interface AttractionServiceClient {
    
    @GetMapping("/api/attraction/{id}")
    ResponseEntity<Object> getAttractionById(@PathVariable("id") UUID id);
    
    @GetMapping("/api/attraction")
    ResponseEntity<List<Object>> getAllAttractions();
    
    @GetMapping("/api/attraction/destination/{destination}")
    ResponseEntity<List<Object>> getAttractionsByDestination(@PathVariable("destination") String destination);
    
    @GetMapping("/api/attraction/category/{category}")
    ResponseEntity<List<Object>> getAttractionsByCategory(@PathVariable("category") String category);
    
    @GetMapping("/api/attraction/rating/{minRating}")
    ResponseEntity<List<Object>> getAttractionsByMinRating(@PathVariable("minRating") BigDecimal minRating);
}