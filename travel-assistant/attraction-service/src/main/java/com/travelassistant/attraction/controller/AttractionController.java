package com.travelassistant.attraction.controller;

import com.travelassistant.attraction.entity.Attraction;
import com.travelassistant.attraction.service.AttractionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/attraction")
@Tag(name = "Attraction Service", description = "景点管理相关的API")
public class AttractionController {

    @Autowired
    private AttractionService attractionService;

    @PostMapping
    @Operation(summary = "创建景点", description = "创建新的景点")
    public ResponseEntity<Attraction> createAttraction(@Valid @RequestBody Attraction attraction) {
        Attraction createdAttraction = attractionService.createAttraction(attraction);
        return new ResponseEntity<>(createdAttraction, HttpStatus.CREATED);
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取景点", description = "根据ID获取景点信息")
    public ResponseEntity<Attraction> getAttractionById(
            @Parameter(description = "景点ID", required = true)
            @PathVariable UUID id) {
        Attraction attraction = attractionService.getAttractionById(id);
        return ResponseEntity.ok(attraction);
    }

    @GetMapping
    @Operation(summary = "获取所有景点", description = "获取所有景点的列表")
    public ResponseEntity<List<Attraction>> getAllAttractions() {
        List<Attraction> attractions = attractionService.getAllAttractions();
        return ResponseEntity.ok(attractions);
    }

    @GetMapping("/destination/{destination}")
    @Operation(summary = "根据目的地获取景点", description = "根据目的地获取景点列表")
    public ResponseEntity<List<Attraction>> getAttractionsByDestination(
            @Parameter(description = "目的地", required = true)
            @PathVariable String destination) {
        List<Attraction> attractions = attractionService.getAttractionsByDestination(destination);
        return ResponseEntity.ok(attractions);
    }

    @GetMapping("/category/{category}")
    @Operation(summary = "根据类别获取景点", description = "根据类别获取景点列表")
    public ResponseEntity<List<Attraction>> getAttractionsByCategory(
            @Parameter(description = "景点类别", required = true)
            @PathVariable String category) {
        List<Attraction> attractions = attractionService.getAttractionsByCategory(category);
        return ResponseEntity.ok(attractions);
    }

    @GetMapping("/rating/{minRating}")
    @Operation(summary = "根据评分获取景点", description = "根据最低评分获取景点列表")
    public ResponseEntity<List<Attraction>> getAttractionsByMinRating(
            @Parameter(description = "最低评分", required = true)
            @PathVariable BigDecimal minRating) {
        List<Attraction> attractions = attractionService.getAttractionsByMinRating(minRating);
        return ResponseEntity.ok(attractions);
    }

    @GetMapping("/tag/{tag}")
    @Operation(summary = "根据标签获取景点", description = "根据指定标签获取景点列表")
    public ResponseEntity<List<Attraction>> getAttractionsByTag(
            @Parameter(description = "标签名称", required = true)
            @PathVariable String tag) {
        List<Attraction> attractions = attractionService.getAttractionsByTag(tag);
        return ResponseEntity.ok(attractions);
    }

    @GetMapping("/tags")
    @Operation(summary = "根据多个标签获取景点", description = "根据多个标签获取景点列表")
    public ResponseEntity<List<Attraction>> getAttractionsByTags(
            @Parameter(description = "标签列表", required = true)
            @RequestParam List<String> tags) {
        List<Attraction> attractions = attractionService.getAttractionsByTags(tags);
        return ResponseEntity.ok(attractions);
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新景点", description = "更新指定ID的景点信息")
    public ResponseEntity<Attraction> updateAttraction(
            @Parameter(description = "景点ID", required = true)
            @PathVariable UUID id,
            @Valid @RequestBody Attraction attraction) {
        Attraction updatedAttraction = attractionService.updateAttraction(id, attraction);
        return ResponseEntity.ok(updatedAttraction);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除景点", description = "删除指定ID的景点")
    public ResponseEntity<Void> deleteAttraction(
            @Parameter(description = "景点ID", required = true)
            @PathVariable UUID id) {
        attractionService.deleteAttraction(id);
        return ResponseEntity.noContent().build();
    }
}