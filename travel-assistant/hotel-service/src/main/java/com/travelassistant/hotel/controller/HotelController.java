package com.travelassistant.hotel.controller;

import com.travelassistant.hotel.entity.Hotel;
import com.travelassistant.hotel.service.HotelService;
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
@RequestMapping("/api/hotel")
@Tag(name = "Hotel Service", description = "酒店管理相关的API")
public class HotelController {

    @Autowired
    private HotelService hotelService;

    @PostMapping
    @Operation(summary = "创建酒店", description = "创建新的酒店")
    public ResponseEntity<Hotel> createHotel(@Valid @RequestBody Hotel hotel) {
        Hotel createdHotel = hotelService.createHotel(hotel);
        return new ResponseEntity<>(createdHotel, HttpStatus.CREATED);
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取酒店", description = "根据ID获取酒店信息")
    public ResponseEntity<Hotel> getHotelById(
            @Parameter(description = "酒店ID", required = true)
            @PathVariable UUID id) {
        Hotel hotel = hotelService.getHotelById(id);
        return ResponseEntity.ok(hotel);
    }

    @GetMapping
    @Operation(summary = "获取所有酒店", description = "获取所有酒店的列表")
    public ResponseEntity<List<Hotel>> getAllHotels() {
        List<Hotel> hotels = hotelService.getAllHotels();
        return ResponseEntity.ok(hotels);
    }

    @GetMapping("/destination/{destination}")
    @Operation(summary = "根据目的地获取酒店", description = "根据目的地获取酒店列表")
    public ResponseEntity<List<Hotel>> getHotelsByDestination(
            @Parameter(description = "目的地", required = true)
            @PathVariable String destination) {
        List<Hotel> hotels = hotelService.getHotelsByDestination(destination);
        return ResponseEntity.ok(hotels);
    }

    @GetMapping("/price-range")
    @Operation(summary = "根据价格范围获取酒店", description = "根据价格范围获取酒店列表")
    public ResponseEntity<List<Hotel>> getHotelsByPriceRange(
            @Parameter(description = "最低价格", required = true)
            @RequestParam BigDecimal minPrice,
            @Parameter(description = "最高价格", required = true)
            @RequestParam BigDecimal maxPrice) {
        List<Hotel> hotels = hotelService.getHotelsByPriceRange(minPrice, maxPrice);
        return ResponseEntity.ok(hotels);
    }

    @GetMapping("/rating/{minRating}")
    @Operation(summary = "根据评分获取酒店", description = "根据最低评分获取酒店列表")
    public ResponseEntity<List<Hotel>> getHotelsByMinRating(
            @Parameter(description = "最低评分", required = true)
            @PathVariable BigDecimal minRating) {
        List<Hotel> hotels = hotelService.getHotelsByMinRating(minRating);
        return ResponseEntity.ok(hotels);
    }

    @GetMapping("/facility/{facility}")
    @Operation(summary = "根据设施获取酒店", description = "根据指定设施获取酒店列表")
    public ResponseEntity<List<Hotel>> getHotelsByFacility(
            @Parameter(description = "设施名称", required = true)
            @PathVariable String facility) {
        List<Hotel> hotels = hotelService.getHotelsByFacility(facility);
        return ResponseEntity.ok(hotels);
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新酒店", description = "更新指定ID的酒店信息")
    public ResponseEntity<Hotel> updateHotel(
            @Parameter(description = "酒店ID", required = true)
            @PathVariable UUID id,
            @Valid @RequestBody Hotel hotel) {
        Hotel updatedHotel = hotelService.updateHotel(id, hotel);
        return ResponseEntity.ok(updatedHotel);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除酒店", description = "删除指定ID的酒店")
    public ResponseEntity<Void> deleteHotel(
            @Parameter(description = "酒店ID", required = true)
            @PathVariable UUID id) {
        hotelService.deleteHotel(id);
        return ResponseEntity.noContent().build();
    }
}