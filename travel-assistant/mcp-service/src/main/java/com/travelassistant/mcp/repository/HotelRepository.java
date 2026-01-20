package com.travelassistant.mcp.repository;

import com.travelassistant.mcp.entity.Hotel;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;

public interface HotelRepository extends JpaRepository<Hotel, Long> {
    @Query("SELECT h FROM Hotel h WHERE h.destination = :destination AND h.price BETWEEN :minPrice AND :maxPrice AND h.rating >= :minRating")
    List<Hotel> searchHotels(@Param("destination") String destination, 
                             @Param("minPrice") Double minPrice, 
                             @Param("maxPrice") Double maxPrice, 
                             @Param("minRating") Double minRating);
}
