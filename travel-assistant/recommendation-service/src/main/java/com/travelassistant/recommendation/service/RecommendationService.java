package com.travelassistant.recommendation.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.travelassistant.hotel.entity.Hotel;
import com.travelassistant.recommendation.client.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class RecommendationService {

    @Autowired
    private UserServiceClient userServiceClient;

    @Autowired
    private HotelServiceClient hotelServiceClient;

    @Autowired
    private FlightServiceClient flightServiceClient;

    @Autowired
    private AttractionServiceClient attractionServiceClient;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * 为用户推荐酒店
     */
    public List<Map<String, Object>> recommendHotels(UUID userId, int limit) {
        try {
            // 获取用户偏好
            Map<String, Object> userPreferences = userServiceClient.getUserPreferences(userId).getBody();
            
            String budgetLevel = (String) userPreferences.get("budget_level");
            List<String> preferredDestinations = (List<String>) userPreferences.get("preferred_destinations");
            
            // 根据预算等级设定价格范围
            BigDecimal minPrice, maxPrice;
            switch (budgetLevel != null ? budgetLevel : "mid") {
                case "budget":
                    minPrice = BigDecimal.valueOf(0);
                    maxPrice = BigDecimal.valueOf(200);
                    break;
                case "luxury":
                    minPrice = BigDecimal.valueOf(500);
                    maxPrice = BigDecimal.valueOf(1000);
                    break;
                default: // mid
                    minPrice = BigDecimal.valueOf(200);
                    maxPrice = BigDecimal.valueOf(500);
            }
            
            // 从目的地列表中获取推荐
            if (preferredDestinations != null && !preferredDestinations.isEmpty()) {
                String destination = preferredDestinations.get(0);
                List<Hotel> hotels = (List<Hotel>) hotelServiceClient.getHotelsByPriceRange(minPrice, maxPrice).getBody();
                List<Hotel> result = hotels.stream()
                        .filter(hotel -> {
                            // 这里需要根据实际数据结构进行过滤
                            return true; // 简化处理
                        })
                        .limit(limit)
                        .collect(Collectors.toList());
                // Convert List<Hotel> to List<Map<String, Object>>
                return result.stream()
                        .map(hotel -> objectMapper.convertValue(hotel, Map.class))
                        .collect(Collectors.toList());
            }
            
            return new ArrayList<>();
        } catch (Exception e) {
            // 返回空列表而不是抛出异常
            return new ArrayList<>();
        }
    }

    /**
     * 为用户推荐航班
     */
    public List<Map<String, Object>> recommendFlights(UUID userId, int limit) {
        try {
            // 获取用户偏好
            Map<String, Object> userPreferences = userServiceClient.getUserPreferences(userId).getBody();
            
            List<String> preferredDestinations = (List<String>) userPreferences.get("preferred_destinations");
            
            if (preferredDestinations != null && !preferredDestinations.isEmpty()) {
                String destination = preferredDestinations.get(0);
                // 这里可以根据实际需求设定出发地
                String origin = "Beijing"; // 默认出发地

                List<Object> flights = flightServiceClient.getFlightsByOriginAndDestination(origin, destination).getBody();
                if (flights != null) {
                    return flights.stream()
                            .limit(limit)
                            .map(flight -> objectMapper.convertValue(flight, Map.class))
                            .collect(Collectors.toList());
                }
            }
            
            return new ArrayList<>();
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }

    /**
     * 为用户推荐景点
     */
    public List<Map<String, Object>> recommendAttractions(UUID userId, int limit) {
        try {
            // 获取用户偏好
            Map<String, Object> userPreferences = userServiceClient.getUserPreferences(userId).getBody();
            
            List<String> interests = (List<String>) userPreferences.get("interests");
            List<String> preferredDestinations = (List<String>) userPreferences.get("preferred_destinations");
            
            List<Map<String, Object>> recommendations = new ArrayList<>();
            
            // 根据兴趣推荐景点
            if (interests != null && !interests.isEmpty()) {
                for (String interest : interests) {
                    try {
                        List<Object> attractionsByTag = attractionServiceClient.getAttractionsByTag(interest).getBody();
                        if (attractionsByTag != null) {
                            // Convert each attraction object to Map
                            recommendations.addAll(attractionsByTag.stream()
                                    .map(attraction -> objectMapper.convertValue(attraction, Map.class))
                                    .collect(Collectors.toList()));
                        }
                    } catch (Exception e) {
                        // 忽略单个标签的错误
                    }
                }
            }

            // 根据目的地推荐景点
            if (preferredDestinations != null && !preferredDestinations.isEmpty()) {
                String destination = preferredDestinations.get(0);
                try {
                    List<Object> attractionsByDestination = attractionServiceClient.getAttractionsByDestination(destination).getBody();
                    if (attractionsByDestination != null) {
                        // Convert each attraction object to Map
                        recommendations.addAll(attractionsByDestination.stream()
                                .map(attraction -> objectMapper.convertValue(attraction, Map.class))
                                .collect(Collectors.toList()));
                    }
                } catch (Exception e) {
                    // 忽略错误
                }
            }
            
            // 去重并限制数量
            return recommendations.stream()
                    .distinct()
                    .limit(limit)
                    .collect(Collectors.toList());
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }

    /**
     * 为用户生成综合推荐
     */
    public Map<String, Object> getComprehensiveRecommendations(UUID userId, int limit) {
        Map<String, Object> recommendations = new HashMap<>();
        
        recommendations.put("hotels", recommendHotels(userId, limit));
        recommendations.put("flights", recommendFlights(userId, limit));
        recommendations.put("attractions", recommendAttractions(userId, limit));
        
        return recommendations;
    }

    /**
     * 根据特定条件推荐景点
     */
    public List<Map<String, Object>> recommendAttractionsByTags(List<String> tags, int limit) {
        try {
            List<Object> attractions = attractionServiceClient.getAttractionsByTags(tags).getBody();
            if (attractions != null) {
                return attractions.stream()
                        .limit(limit)
                        .map(attraction -> objectMapper.convertValue(attraction, Map.class))
                        .collect(Collectors.toList());
            }
            return new ArrayList<>();
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }

    /**
     * 根据目的地推荐景点
     */
    public List<Map<String, Object>> recommendAttractionsByDestination(String destination, int limit) {
        try {
            List<Object> attractions = attractionServiceClient.getAttractionsByDestination(destination).getBody();
            if (attractions != null) {
                return attractions.stream()
                        .limit(limit)
                        .map(attraction -> objectMapper.convertValue(attraction, Map.class))
                        .collect(Collectors.toList());
            }
            return new ArrayList<>();
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }
}