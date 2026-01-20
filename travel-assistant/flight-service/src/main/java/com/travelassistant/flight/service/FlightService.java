package com.travelassistant.flight.service;

import com.travelassistant.flight.entity.Flight;
import com.travelassistant.flight.repository.FlightRepository;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@Service
@Transactional
public class FlightService {

    @Autowired
    private FlightRepository flightRepository;

    /**
     * 创建航班
     */
    public Flight createFlight(Flight flight) {
        return flightRepository.save(flight);
    }

    /**
     * 根据ID获取航班
     */
    public Flight getFlightById(UUID id) {
        return flightRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Flight not found with id: " + id));
    }

    /**
     * 获取所有航班
     */
    public List<Flight> getAllFlights() {
        return flightRepository.findAll();
    }

    /**
     * 根据出发地和目的地获取航班
     */
    public List<Flight> getFlightsByOriginAndDestination(String origin, String destination) {
        return flightRepository.findByOriginAndDestination(origin, destination);
    }

    /**
     * 根据出发日期获取航班
     */
    public List<Flight> getFlightsByDepartureDate(LocalDate departureDate) {
        return flightRepository.findByDepartureDate(departureDate);
    }

    /**
     * 根据航空公司获取航班
     */
    public List<Flight> getFlightsByAirline(String airline) {
        return flightRepository.findByAirline(airline);
    }

    /**
     * 根据价格范围获取航班
     */
    public List<Flight> getFlightsByPriceRange(BigDecimal minPrice, BigDecimal maxPrice) {
        return flightRepository.findByPriceRange(minPrice, maxPrice);
    }

    /**
     * 根据出发地、目的地和日期获取航班
     */
    public List<Flight> getFlightsByOriginDestinationAndDate(String origin, String destination, LocalDate departureDate) {
        return flightRepository.findByOriginDestinationAndDate(origin, destination, departureDate);
    }

    /**
     * 根据出发地和日期范围获取航班
     */
    public List<Flight> getFlightsByOriginAndDateRange(String origin, LocalDate startDate, LocalDate endDate) {
        return flightRepository.findByOriginAndDateRange(origin, startDate, endDate);
    }

    /**
     * 更新航班
     */
    public Flight updateFlight(UUID id, Flight updatedFlight) {
        Flight existingFlight = getFlightById(id);
        // 更新字段逻辑
        return flightRepository.save(existingFlight);
    }

    /**
     * 删除航班
     */
    public void deleteFlight(UUID id) {
        Flight flight = getFlightById(id);
        flightRepository.delete(flight);
    }
}