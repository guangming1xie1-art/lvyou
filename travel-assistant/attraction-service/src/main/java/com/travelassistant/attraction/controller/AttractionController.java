package com.travelassistant.attraction.controller;

import com.travelassistant.attraction.dto.AttractionSearchCriteria;
import com.travelassistant.attraction.dto.PageResponse;
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
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;

@RestController
@RequestMapping("/api/attraction")
@Tag(name = "Attraction Service", description = "景点管理相关的API")
public class AttractionController {

    @Autowired
    private AttractionService attractionService;

    /**
     * 通用搜索端点 - 支持任意参数组合的可选参数查询
     * 所有参数都是可选的，可以任意组合使用
     */
    @GetMapping("/search")
    @Operation(
            summary = "搜索景点（动态查询）",
            description = "通用搜索端点，支持任意参数组合的可选参数查询。" +
                    "所有参数都是可选的，可以传一个、多个或全部参数。" +
                    "支持：destination, name, category, minRating, maxRating, tags, " +
                    "description, openingHours, 分页和排序"
    )
    public ResponseEntity<List<Attraction>> searchAttractions(
            // ✅ 改成 Page<Attraction>
            @Parameter(description = "目的地")
            @RequestParam(name="destination", required = false) String destination,

            @Parameter(description = "景点名称（模糊匹配）")
            @RequestParam(name="name", required = false) String name,

            @Parameter(description = "类别")
            @RequestParam(name="category", required = false) String category,

            @Parameter(description = "最低评分")
            @RequestParam(name="minRating", required = false) BigDecimal minRating,

            @Parameter(description = "最高评分")
            @RequestParam(name="maxRating", required = false) BigDecimal maxRating,

            @Parameter(description = "标签列表（满足任一即可）")
            @RequestParam(name="tags", required = false) List<String> tags,

            @Parameter(description = "描述关键词（模糊匹配）")
            @RequestParam(name="description", required = false) String description,

            @Parameter(description = "营业时间")
            @RequestParam(name="openingHours", required = false) String openingHours,

            @Parameter(description = "排序字段: name, rating, category, createdAt")
            @RequestParam(name="sortBy", defaultValue = "createdAt") String sortBy,

            @Parameter(description = "排序方向: asc, desc")
            @RequestParam(name="sortDirection", defaultValue = "desc") String sortDirection,

            // ✅ 改成 Pageable，Spring 自动处理
            @Parameter(description = "分页参数")
            @PageableDefault(page = 0, size = 10) Pageable pageable) {

        AttractionSearchCriteria criteria = AttractionSearchCriteria.builder()
                .destination(destination)
                .name(name)
                .category(category)
                .minRating(minRating)
                .maxRating(maxRating)
                .tags(tags)
                .description(description)
                .openingHours(openingHours)
                .sortBy(sortBy)
                .sortDirection(sortDirection)
                .build();

        // ✅ 直接返回 Page
        Page<Attraction> result = attractionService.searchAttractions(criteria, pageable);
        return ResponseEntity.ok(result.getContent());
    }

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