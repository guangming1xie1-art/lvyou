package com.travelassistant.recommendation.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@FeignClient(name = "hotel-service")
public interface HotelServiceClient {
    
    @GetMapping("/api/hotel/{id}")
    ResponseEntity<Object> getHotelById(@PathVariable("id") UUID id);
    
    @GetMapping("/api/hotel")
    ResponseEntity<List<Object>> getAllHotels();
    
    @GetMapping("/api/hotel/destination/{destination}")
    ResponseEntity<List<Object>> getHotelsByDestination(@PathVariable("destination") String destination);
    
    @GetMapping("/api/hotel/price-range")
    ResponseEntity<List<Object>> getHotelsByPriceRange(
        @RequestParam("minPrice") BigDecimal minPrice,
        @RequestParam("maxPrice") BigDecimal maxPrice);
}