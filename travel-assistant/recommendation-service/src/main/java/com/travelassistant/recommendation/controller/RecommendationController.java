package com.travelassistant.recommendation.controller;

import com.travelassistant.recommendation.service.RecommendationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/recommendation")
@Tag(name = "Recommendation Service", description = "推荐管理相关的API")
public class RecommendationController {

    @Autowired
    private RecommendationService recommendationService;

    @GetMapping("/hotels/{userId}")
    @Operation(summary = "推荐酒店", description = "根据用户偏好推荐酒店")
    public ResponseEntity<List<Map<String, Object>>> recommendHotels(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID userId,
            @Parameter(description = "推荐数量限制", required = false)
            @RequestParam(defaultValue = "10") int limit) {
        List<Map<String, Object>> recommendations = recommendationService.recommendHotels(userId, limit);
        return ResponseEntity.ok(recommendations);
    }

    @GetMapping("/flights/{userId}")
    @Operation(summary = "推荐航班", description = "根据用户偏好推荐航班")
    public ResponseEntity<List<Map<String, Object>>> recommendFlights(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID userId,
            @Parameter(description = "推荐数量限制", required = false)
            @RequestParam(defaultValue = "10") int limit) {
        List<Map<String, Object>> recommendations = recommendationService.recommendFlights(userId, limit);
        return ResponseEntity.ok(recommendations);
    }

    @GetMapping("/attractions/{userId}")
    @Operation(summary = "推荐景点", description = "根据用户偏好推荐景点")
    public ResponseEntity<List<Map<String, Object>>> recommendAttractions(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID userId,
            @Parameter(description = "推荐数量限制", required = false)
            @RequestParam(defaultValue = "10") int limit) {
        List<Map<String, Object>> recommendations = recommendationService.recommendAttractions(userId, limit);
        return ResponseEntity.ok(recommendations);
    }

    @GetMapping("/comprehensive/{userId}")
    @Operation(summary = "综合推荐", description = "为用户生成综合推荐（酒店、航班、景点）")
    public ResponseEntity<Map<String, Object>> getComprehensiveRecommendations(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID userId,
            @Parameter(description = "推荐数量限制", required = false)
            @RequestParam(defaultValue = "10") int limit) {
        Map<String, Object> recommendations = recommendationService.getComprehensiveRecommendations(userId, limit);
        return ResponseEntity.ok(recommendations);
    }

    @GetMapping("/attractions/tags")
    @Operation(summary = "根据标签推荐景点", description = "根据指定的标签列表推荐景点")
    public ResponseEntity<List<Map<String, Object>>> recommendAttractionsByTags(
            @Parameter(description = "标签列表", required = true)
            @RequestParam List<String> tags,
            @Parameter(description = "推荐数量限制", required = false)
            @RequestParam(defaultValue = "10") int limit) {
        List<Map<String, Object>> recommendations = recommendationService.recommendAttractionsByTags(tags, limit);
        return ResponseEntity.ok(recommendations);
    }

    @GetMapping("/attractions/destination/{destination}")
    @Operation(summary = "根据目的地推荐景点", description = "根据指定的目的地推荐景点")
    public ResponseEntity<List<Map<String, Object>>> recommendAttractionsByDestination(
            @Parameter(description = "目的地", required = true)
            @PathVariable String destination,
            @Parameter(description = "推荐数量限制", required = false)
            @RequestParam(defaultValue = "10") int limit) {
        List<Map<String, Object>> recommendations = recommendationService.recommendAttractionsByDestination(destination, limit);
        return ResponseEntity.ok(recommendations);
    }
}