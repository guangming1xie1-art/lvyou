package com.travelassistant.mcp.repository;

import com.travelassistant.mcp.entity.Flight;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface FlightRepository extends JpaRepository<Flight, Long> {
    List<Flight> findByOriginAndDestination(String origin, String destination);
}
