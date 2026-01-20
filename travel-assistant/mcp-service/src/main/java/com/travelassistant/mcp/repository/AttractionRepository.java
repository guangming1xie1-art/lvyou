package com.travelassistant.mcp.repository;

import com.travelassistant.mcp.entity.Attraction;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface AttractionRepository extends JpaRepository<Attraction, Long> {
    List<Attraction> findByDestination(String destination);
}
