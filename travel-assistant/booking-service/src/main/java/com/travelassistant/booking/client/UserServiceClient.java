package com.travelassistant.booking.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@FeignClient(name = "user-service")
public interface UserServiceClient {
    
    @GetMapping("/api/user/{id}")
    ResponseEntity<Object> getUserById(@PathVariable("id") UUID id);
    
    @GetMapping("/api/user/email/{email}")
    ResponseEntity<Object> getUserByEmail(@PathVariable("email") String email);
}