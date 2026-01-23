package com.travelassistant.auth.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class LoginResponse {
    private UserResponse user;
    private TokenResponse tokens;
    
    public LoginResponse(UserResponse user, TokenResponse tokens) {
        this.user = user;
        this.tokens = tokens;
    }
}