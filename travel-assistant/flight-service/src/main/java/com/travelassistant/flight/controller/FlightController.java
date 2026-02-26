package com.travelassistant.flight.controller;

import com.travelassistant.flight.entity.Flight;
import com.travelassistant.flight.service.FlightService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/flight")
@Tag(name = "Flight Service", description = "航班管理相关的API")
public class FlightController {

    @Autowired
    private FlightService flightService;

    @PostMapping
    @Operation(summary = "创建航班", description = "创建新的航班")
    public ResponseEntity<Flight> createFlight(@Valid @RequestBody Flight flight) {
        Flight createdFlight = flightService.createFlight(flight);
        return new ResponseEntity<>(createdFlight, HttpStatus.CREATED);
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取航班", description = "根据ID获取航班信息")
    public ResponseEntity<Flight> getFlightById(
            @Parameter(description = "航班ID", required = true)
            @PathVariable UUID id) {
        Flight flight = flightService.getFlightById(id);
        return ResponseEntity.ok(flight);
    }

    @GetMapping
    @Operation(summary = "获取所有航班", description = "获取所有航班的列表")
    public ResponseEntity<List<Flight>> getAllFlights() {
        List<Flight> flights = flightService.getAllFlights();
        return ResponseEntity.ok(flights);
    }

    @GetMapping("/route/{origin}/{destination}")
    @Operation(summary = "根据航线获取航班", description = "根据出发地和目的地获取航班列表")
    public ResponseEntity<List<Flight>> getFlightsByOriginAndDestination(
            @Parameter(description = "出发地", required = true)
            @PathVariable String origin,
            @Parameter(description = "目的地", required = true)
            @PathVariable String destination) {
        List<Flight> flights = flightService.getFlightsByOriginAndDestination(origin, destination);
        return ResponseEntity.ok(flights);
    }

    @GetMapping("/date/{departureDate}")
    @Operation(summary = "根据出发日期获取航班", description = "根据出发日期获取航班列表")
    public ResponseEntity<List<Flight>> getFlightsByDepartureDate(
            @Parameter(description = "出发日期", required = true)
            @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate departureDate) {
        List<Flight> flights = flightService.getFlightsByDepartureDate(departureDate);
        return ResponseEntity.ok(flights);
    }

    @GetMapping("/airline/{airline}")
    @Operation(summary = "根据航空公司获取航班", description = "根据航空公司获取航班列表")
    public ResponseEntity<List<Flight>> getFlightsByAirline(
            @Parameter(description = "航空公司", required = true)
            @PathVariable String airline) {
        List<Flight> flights = flightService.getFlightsByAirline(airline);
        return ResponseEntity.ok(flights);
    }

    @GetMapping("/price-range")
    @Operation(summary = "根据价格范围获取航班", description = "根据价格范围获取航班列表")
    public ResponseEntity<List<Flight>> getFlightsByPriceRange(
            @Parameter(description = "最低价格", required = true)
            @RequestParam BigDecimal minPrice,
            @Parameter(description = "最高价格", required = true)
            @RequestParam BigDecimal maxPrice) {
        List<Flight> flights = flightService.getFlightsByPriceRange(minPrice, maxPrice);
        return ResponseEntity.ok(flights);
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新航班", description = "更新指定ID的航班信息")
    public ResponseEntity<Flight> updateFlight(
            @Parameter(description = "航班ID", required = true)
            @PathVariable UUID id,
            @Valid @RequestBody Flight flight) {
        Flight updatedFlight = flightService.updateFlight(id, flight);
        return ResponseEntity.ok(updatedFlight);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除航班", description = "删除指定ID的航班")
    public ResponseEntity<Void> deleteFlight(
            @Parameter(description = "航班ID", required = true)
            @PathVariable UUID id) {
        flightService.deleteFlight(id);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/flight_info")
    @Operation(summary = "根据航线获取航班", description = "根据出发地和目的地获取航班列表")
    public ResponseEntity<List<Flight>> getFlightsByOriginAndDestinationAndDate(
            @Parameter(description = "出发地", required = true)
            @PathVariable String origin,
            @Parameter(description = "目的地", required = true)
            @PathVariable String destination,
            @Parameter(description = "起飞日", required = true)
            @PathVariable LocalDate destinationDate) {
        List<Flight> flights1 = flightService.getFlightsByOriginDestinationAndDate(origin, destination, destinationDate);
        List<Flight> flights2 = flightService.getFlightsInfo(origin, destination, destinationDate);
        flights1.addAll(flights2);
        return ResponseEntity.ok(flights1);
    }
}