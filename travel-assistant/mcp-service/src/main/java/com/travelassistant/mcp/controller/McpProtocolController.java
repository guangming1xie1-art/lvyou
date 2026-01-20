package com.travelassistant.mcp.controller;

import com.travelassistant.mcp.dto.RecommendRequest;
import com.travelassistant.mcp.dto.SearchAttractionRequest;
import com.travelassistant.mcp.dto.SearchFlightRequest;
import com.travelassistant.mcp.dto.SearchHotelRequest;
import com.travelassistant.mcp.service.RecommendService;
import com.travelassistant.mcp.service.SearchService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/mcp")
@RequiredArgsConstructor
public class McpProtocolController {
    private final SearchService searchService;
    private final RecommendService recommendService;

    @PostMapping("/search-hotels")
    public Map<String, Object> searchHotels(@RequestBody SearchHotelRequest request) {
        return success(searchService.searchHotels(request));
    }

    @PostMapping("/search-flights")
    public Map<String, Object> searchFlights(@RequestBody SearchFlightRequest request) {
        return success(searchService.searchFlights(request));
    }

    @PostMapping("/search-attractions")
    public Map<String, Object> searchAttractions(@RequestBody SearchAttractionRequest request) {
        return success(searchService.searchAttractions(request));
    }

    @PostMapping("/get-recommendation-base")
    public Map<String, Object> getRecommendationBase(@RequestBody RecommendRequest request) {
        return success(recommendService.getRecommendationBase(request));
    }

    private Map<String, Object> success(Object data) {
        Map<String, Object> response = new HashMap<>();
        response.put("code", 0);
        response.put("data", data);
        response.put("message", "success");
        return response;
    }
}
