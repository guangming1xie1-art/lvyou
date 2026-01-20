package com.travelassistant.mcp.service;

import com.travelassistant.mcp.dto.RecommendRequest;
import com.travelassistant.mcp.entity.Attraction;
import com.travelassistant.mcp.entity.Hotel;
import com.travelassistant.mcp.entity.User;
import com.travelassistant.mcp.repository.AttractionRepository;
import com.travelassistant.mcp.repository.HotelRepository;
import com.travelassistant.mcp.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class RecommendService {
    private final HotelRepository hotelRepository;
    private final AttractionRepository attractionRepository;
    private final UserRepository userRepository;

    public Map<String, Object> getRecommendationBase(RecommendRequest request) {
        Map<String, Object> result = new HashMap<>();
        
        userRepository.findByEmail(request.getEmail()).ifPresent(user -> result.put("user", user));
        
        List<Hotel> hotels = hotelRepository.searchHotels(request.getDestination(), 0.0, Double.MAX_VALUE, 4.0);
        List<Attraction> attractions = attractionRepository.findByDestination(request.getDestination());
        
        result.put("hotels", hotels);
        result.put("attractions", attractions);
        
        return result;
    }
}
