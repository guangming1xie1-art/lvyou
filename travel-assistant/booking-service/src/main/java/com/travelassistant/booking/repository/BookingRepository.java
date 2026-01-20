package com.travelassistant.booking.repository;

import com.travelassistant.booking.entity.Booking;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Repository
public interface BookingRepository extends JpaRepository<Booking, UUID> {

  /**
   * 根据用户ID查找预订
   */
  List<Booking> findByUserId(UUID userId);

  /**
   * 根据预订类型查找预订
   */
  List<Booking> findByBookingType(String bookingType);

  /**
   * 根据资源ID查找预订
   */
  List<Booking> findByResourceId(UUID resourceId);

  /**
   * 根据状态查找预订
   */
  List<Booking> findByStatus(String status);

  /**
   * 根据用户ID和状态查找预订
   */
  @Query("SELECT b FROM Booking b WHERE b.userId = :userId AND b.status = :status")
  List<Booking> findByUserIdAndStatus(@Param("userId") UUID userId, @Param("status") String status);

  /**
   * 根据预订类型和状态查找预订
   */
  @Query("SELECT b FROM Booking b WHERE b.bookingType = :bookingType AND b.status = :status")
  List<Booking> findByBookingTypeAndStatus(@Param("bookingType") String bookingType, @Param("status") String status);

  /**
   * 根据预订日期范围查找预订
   */
  @Query("SELECT b FROM Booking b WHERE b.bookingDate BETWEEN :startDate AND :endDate")
  List<Booking> findByBookingDateBetween(@Param("startDate") LocalDateTime startDate, @Param("endDate") LocalDateTime endDate);
}