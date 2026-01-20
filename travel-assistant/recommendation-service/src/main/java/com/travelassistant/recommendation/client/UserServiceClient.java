package com.travelassistant.recommendation.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@FeignClient(name = "user-service")
public interface UserServiceClient {
    
    @GetMapping("/api/user/{id}")
    ResponseEntity<Object> getUserById(@PathVariable("id") UUID id);
    
    @GetMapping("/api/user/{id}/preferences")
    ResponseEntity<Map<String, Object>> getUserPreferences(@PathVariable("id") UUID id);
    
    @GetMapping("/api/user/email/{email}")
    ResponseEntity<Object> getUserByEmail(@PathVariable("email") String email);
}