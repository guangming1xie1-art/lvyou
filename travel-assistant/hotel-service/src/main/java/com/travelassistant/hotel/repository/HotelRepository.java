package com.travelassistant.hotel.repository;

import com.travelassistant.hotel.entity.Hotel;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@Repository
public interface HotelRepository extends JpaRepository<Hotel, UUID> {

  /**
   * 根据目的地查找酒店
   */
  List<Hotel> findByDestination(String destination);

  /**
   * 根据价格范围查找酒店
   */
  @Query("SELECT h FROM Hotel h WHERE h.price BETWEEN :minPrice AND :maxPrice")
  List<Hotel> findByPriceRange(@Param("minPrice") BigDecimal minPrice, @Param("maxPrice") BigDecimal maxPrice);

  /**
   * 根据评分查找酒店
   */
  @Query("SELECT h FROM Hotel h WHERE h.rating >= :minRating ORDER BY h.rating DESC")
  List<Hotel> findByMinRating(@Param("minRating") BigDecimal minRating);

  /**
   * 根据目的地和价格范围查找酒店
   */
  @Query("SELECT h FROM Hotel h WHERE h.destination = :destination AND h.price BETWEEN :minPrice AND :maxPrice")
  List<Hotel> findByDestinationAndPriceRange(
      @Param("destination") String destination,
      @Param("minPrice") BigDecimal minPrice,
      @Param("maxPrice") BigDecimal maxPrice);

  /**
   * 根据设施查找酒店
   */
  @Query("SELECT h FROM Hotel h WHERE :facility = ANY(h.facilities)")
  List<Hotel> findByFacility(@Param("facility") String facility);

  /**
   * 根据评分范围查找酒店
   */
  @Query("SELECT h FROM Hotel h WHERE h.rating BETWEEN :minRating AND :maxRating")
  List<Hotel> findByRatingRange(@Param("minRating") BigDecimal minRating, @Param("maxRating") BigDecimal maxRating);
}