package com.travelassistant.booking.controller;

import com.travelassistant.booking.entity.Booking;
import com.travelassistant.booking.service.BookingService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/booking")
@Tag(name = "Booking Service", description = "预订管理相关的API")
public class BookingController {

    @Autowired
    private BookingService bookingService;

    @PostMapping
    @Operation(summary = "创建预订", description = "创建新的预订")
    public ResponseEntity<Booking> createBooking(@Valid @RequestBody Booking booking) {
        Booking createdBooking = bookingService.createBooking(booking);
        return new ResponseEntity<>(createdBooking, HttpStatus.CREATED);
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取预订", description = "根据ID获取预订信息")
    public ResponseEntity<Booking> getBookingById(
            @Parameter(description = "预订ID", required = true)
            @PathVariable UUID id) {
        Booking booking = bookingService.getBookingById(id);
        return ResponseEntity.ok(booking);
    }

    @GetMapping
    @Operation(summary = "获取所有预订", description = "获取所有预订的列表")
    public ResponseEntity<List<Booking>> getAllBookings() {
        List<Booking> bookings = bookingService.getAllBookings();
        return ResponseEntity.ok(bookings);
    }

    @GetMapping("/user/{userId}")
    @Operation(summary = "根据用户获取预订", description = "根据用户ID获取预订列表")
    public ResponseEntity<List<Booking>> getBookingsByUserId(
            @Parameter(description = "用户ID", required = true)
            @PathVariable UUID userId) {
        List<Booking> bookings = bookingService.getBookingsByUserId(userId);
        return ResponseEntity.ok(bookings);
    }

    @GetMapping("/type/{bookingType}")
    @Operation(summary = "根据类型获取预订", description = "根据预订类型获取预订列表")
    public ResponseEntity<List<Booking>> getBookingsByBookingType(
            @Parameter(description = "预订类型", required = true)
            @PathVariable String bookingType) {
        List<Booking> bookings = bookingService.getBookingsByBookingType(bookingType);
        return ResponseEntity.ok(bookings);
    }

    @GetMapping("/status/{status}")
    @Operation(summary = "根据状态获取预订", description = "根据状态获取预订列表")
    public ResponseEntity<List<Booking>> getBookingsByStatus(
            @Parameter(description = "预订状态", required = true)
            @PathVariable String status) {
        List<Booking> bookings = bookingService.getBookingsByStatus(status);
        return ResponseEntity.ok(bookings);
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新预订", description = "更新指定ID的预订信息")
    public ResponseEntity<Booking> updateBooking(
            @Parameter(description = "预订ID", required = true)
            @PathVariable UUID id,
            @Valid @RequestBody Booking booking) {
        Booking updatedBooking = bookingService.updateBooking(id, booking);
        return ResponseEntity.ok(updatedBooking);
    }

    @PutMapping("/{id}/cancel")
    @Operation(summary = "取消预订", description = "取消指定ID的预订")
    public ResponseEntity<Booking> cancelBooking(
            @Parameter(description = "预订ID", required = true)
            @PathVariable UUID id) {
        Booking cancelledBooking = bookingService.cancelBooking(id);
        return ResponseEntity.ok(cancelledBooking);
    }

    @PutMapping("/{id}/confirm")
    @Operation(summary = "确认预订", description = "确认指定ID的预订")
    public ResponseEntity<Booking> confirmBooking(
            @Parameter(description = "预订ID", required = true)
            @PathVariable UUID id) {
        Booking confirmedBooking = bookingService.confirmBooking(id);
        return ResponseEntity.ok(confirmedBooking);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除预订", description = "删除指定ID的预订")
    public ResponseEntity<Void> deleteBooking(
            @Parameter(description = "预订ID", required = true)
            @PathVariable UUID id) {
        bookingService.deleteBooking(id);
        return ResponseEntity.noContent().build();
    }
}