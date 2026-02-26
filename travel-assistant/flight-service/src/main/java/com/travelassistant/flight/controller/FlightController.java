package com.travelassistant.flight.controller;

import com.travelassistant.flight.DTO.FlightSearchRequest;
import com.travelassistant.flight.dto.FlightSearchCriteria;
import com.travelassistant.flight.dto.PageResponse;
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

    /**
     * 通用搜索端点 - 支持任意参数组合的可选参数查询
     * 所有参数都是可选的，可以任意组合使用
     */
    @GetMapping("/search")
    @Operation(
        summary = "搜索航班（动态查询）",
        description = "通用搜索端点，支持任意参数组合的可选参数查询。" +
                      "所有参数都是可选的，可以传一个、多个或全部参数。" +
                      "支持：origin, destination, departureDateStart/End, returnDateStart/End, " +
                      "minPrice, maxPrice, airline, flightNo, minDuration, maxDuration, 分页和排序"
    )
    public ResponseEntity<List<Flight>> searchFlights(
            @Parameter(description = "出发地")
            @RequestParam(name="origin", required = false) String origin,

            @Parameter(description = "目的地")
            @RequestParam(name="destination", required = false) String destination,

            @Parameter(description = "出发日期开始范围")
            @RequestParam(name="departureDateStart", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate departureDateStart,

            @Parameter(description = "出发日期结束范围")
            @RequestParam(name="departureDateEnd", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate departureDateEnd,

            @Parameter(description = "返回日期开始范围")
            @RequestParam(name="returnDateStart", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate returnDateStart,

            @Parameter(description = "返回日期结束范围")
            @RequestParam(name="returnDateEnd", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate returnDateEnd,

            @Parameter(description = "最低价格")
            @RequestParam(name="minPrice", required = false) BigDecimal minPrice,

            @Parameter(description = "最高价格")
            @RequestParam(name="maxPrice", required = false) BigDecimal maxPrice,

            @Parameter(description = "航空公司")
            @RequestParam(name="airline", required = false) String airline,

            @Parameter(description = "航班号（模糊匹配）")
            @RequestParam(name="flightNo", required = false) String flightNo,

            @Parameter(description = "最短时长（分钟）")
            @RequestParam(name="minDuration", required = false) Integer minDuration,

            @Parameter(description = "最长时长（分钟）")
            @RequestParam(name="maxDuration", required = false) Integer maxDuration,

            @Parameter(description = "排序字段: flightNo, origin, destination, departureDate, price, airline, duration, createdAt")
            @RequestParam(name="sortBy", defaultValue = "createdAt") String sortBy,

            @Parameter(description = "排序方向: asc, desc")
            @RequestParam(name="sortDirection", defaultValue = "desc") String sortDirection,

            @Parameter(description = "页码，从0开始")
            @RequestParam(name="page", defaultValue = "0") Integer page,

            @Parameter(description = "每页大小")
            @RequestParam(name="size", defaultValue = "10") Integer size) {

        FlightSearchCriteria criteria = FlightSearchCriteria.builder()
                .origin(origin)
                .destination(destination)
                .departureDateStart(departureDateStart)
                .departureDateEnd(departureDateEnd)
                .returnDateStart(returnDateStart)
                .returnDateEnd(returnDateEnd)
                .minPrice(minPrice)
                .maxPrice(maxPrice)
                .airline(airline)
                .flightNo(flightNo)
                .minDuration(minDuration)
                .maxDuration(maxDuration)
                .sortBy(sortBy)
                .sortDirection(sortDirection)
                .page(page)
                .size(size)
                .build();

        PageResponse<Flight> result = flightService.searchFlights(criteria);
        return ResponseEntity.ok(result.getContent());
    }

    /**
     * POST版本的搜索端点 - 支持更复杂的查询条件
     */
    @PostMapping("/search")
    @Operation(
        summary = "搜索航班（POST版本）",
        description = "POST版本的通用搜索端点，支持更复杂的查询条件。",
        hidden = true
    )
    public ResponseEntity<PageResponse<Flight>> searchFlightsPost(@RequestBody FlightSearchCriteria criteria) {
        PageResponse<Flight> result = flightService.searchFlights(criteria);
        return ResponseEntity.ok(result);
    }

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
            @Parameter(description = "查询参数")
            @RequestBody FlightSearchRequest request) {
        List<Flight> flights1 = flightService.getFlightsByOriginDestinationAndDate(
                request.getOrigin(),
                request.getDestination(),
                request.getDepartureDate()
        );
        List<Flight> flights2 = flightService.getFlightsInfo(
                request.getOrigin(),
                request.getDestination(),
                request.getDepartureDate()
        );
        flights1.addAll(flights2);
        return ResponseEntity.ok(flights1);
    }
}