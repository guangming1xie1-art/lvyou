package com.travelassistant.flight.service;

import com.travelassistant.flight.entity.Flight;
import com.travelassistant.flight.repository.FlightRepository;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Duration;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

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
        return flightRepository.findByOriginAndDestinationAndDate(origin, destination, departureDate);
    }

    /**
     * 根据出发地和日期范围获取航班
     */
    public List<Flight> getFlightsInfo(String origin, String destination, LocalDate departureDate) {

        // 1. 查询所有从出发地起飞的航班（第一段）
        List<Flight> firstLegFlights = flightRepository.findByOriginAndDepartureDate(origin, departureDate);

        // 2. 查询所有到达目的地的航班（第二段）
        List<Flight> secondLegFlights = flightRepository.findByDestinationAndDepartureDate(destination, departureDate);

        List<Flight> results = new ArrayList<>();

        // 3. 找直达航班（两个列表的交集）
        Set<String> secondLegFlightNos = secondLegFlights.stream()
                .map(Flight::getFlightNo)
                .collect(Collectors.toSet());

        List<Flight> directFlights = firstLegFlights.stream()
                .filter(f -> secondLegFlightNos.contains(f.getFlightNo()))
                .collect(Collectors.toList());

        results.addAll(directFlights);

        // 4. 找转机航班（第一段.destination == 第二段.origin，且时间衔接合理）
        for (Flight first : firstLegFlights) {
            for (Flight second : secondLegFlights) {
                // 同一航班号的是直达，跳过
                if (first.getFlightNo().equals(second.getFlightNo())) {
                    continue;
                }
                // 中转城市匹配
                if (first.getDestination().equals(second.getOrigin())) {
                    // 检查中转时间（比如 1-4 小时）
                    Duration transferTime = Duration.between(first.getDepartureDate(), second.getDepartureDate());
                    if (transferTime.toMinutes() >= 60 && transferTime.toMinutes() <= 240) {
                        results.add(first);
                        results.add(second);
                    }
                }
            }
        }

        // 5. 按总时长排序
        results.sort(Comparator.comparing(Flight::getDepartureDate));

        return results;


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