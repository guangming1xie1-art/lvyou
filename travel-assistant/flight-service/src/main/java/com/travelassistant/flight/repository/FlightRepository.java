package com.travelassistant.flight.repository;

import com.travelassistant.flight.entity.Flight;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@Repository
public interface FlightRepository extends JpaRepository<Flight, UUID> {

  /**
   * 根据出发地和目的地查找航班
   */
  @Query("SELECT f FROM Flight f WHERE f.origin = :origin AND f.destination = :destination")
  List<Flight> findByOriginAndDestination(@Param("origin") String origin, @Param("destination") String destination);

  /**
   * 根据出发日期查找航班
   */
  List<Flight> findByDepartureDate(LocalDate departureDate);

  /**
   * 根据航空公司查找航班
   */
  List<Flight> findByAirline(String airline);

  /**
   * 根据价格范围查找航班
   */
  @Query("SELECT f FROM Flight f WHERE f.price BETWEEN :minPrice AND :maxPrice")
  List<Flight> findByPriceRange(@Param("minPrice") BigDecimal minPrice, @Param("maxPrice") BigDecimal maxPrice);

  /**
   * 根据出发地、目的地和日期查找航班
   */
  @Query("SELECT f FROM Flight f WHERE f.origin = :origin AND f.destination = :destination AND f.departureDate = :departureDate")
  List<Flight> findByOriginAndDestinationAndDate(
      @Param("origin") String origin,
      @Param("destination") String destination,
      @Param("departureDate") LocalDate departureDate);

  /**
   * 根据出发地和日期范围查找航班
   */
  @Query("SELECT f FROM Flight f WHERE f.origin = :origin AND f.departureDate =:departureDate")
  List<Flight> findByOriginAndDepartureDate(
      @Param("origin") String origin,
      @Param("departureDate") LocalDate departureDate);

  /**
   * 根据目的地和日期范围查找航班
   */
  @Query("SELECT f FROM Flight f WHERE f.destination = :destination AND f.departureDate =:departureDate")
  List<Flight> findByDestinationAndDepartureDate(
          @Param("destination") String destination,
          @Param("departureDate") LocalDate departureDate);
}