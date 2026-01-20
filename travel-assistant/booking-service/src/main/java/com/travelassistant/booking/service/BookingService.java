package com.travelassistant.booking.service;

import com.travelassistant.booking.entity.Booking;
import com.travelassistant.booking.repository.BookingRepository;
import com.travelassistant.booking.client.*;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@Transactional
public class BookingService {

    @Autowired
    private BookingRepository bookingRepository;

    @Autowired
    private UserServiceClient userServiceClient;

    @Autowired
    private HotelServiceClient hotelServiceClient;

    @Autowired
    private FlightServiceClient flightServiceClient;

    @Autowired
    private AttractionServiceClient attractionServiceClient;

    /**
     * 创建预订
     */
    public Booking createBooking(Booking booking) {
        // 验证用户是否存在
        validateUserExists(booking.getUserId());
        
        // 验证资源是否存在
        validateResourceExists(booking.getBookingType(), booking.getResourceId());
        
        // 设置默认值
        if (booking.getStatus() == null) {
            booking.setStatus("PENDING");
        }
        if (booking.getBookingDate() == null) {
            booking.setBookingDate(LocalDateTime.now());
        }
        
        return bookingRepository.save(booking);
    }

    /**
     * 根据ID获取预订
     */
    public Booking getBookingById(UUID id) {
        return bookingRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Booking not found with id: " + id));
    }

    /**
     * 获取所有预订
     */
    public List<Booking> getAllBookings() {
        return bookingRepository.findAll();
    }

    /**
     * 根据用户ID获取预订
     */
    public List<Booking> getBookingsByUserId(UUID userId) {
        return bookingRepository.findByUserId(userId);
    }

    /**
     * 根据预订类型获取预订
     */
    public List<Booking> getBookingsByBookingType(String bookingType) {
        return bookingRepository.findByBookingType(bookingType);
    }

    /**
     * 根据状态获取预订
     */
    public List<Booking> getBookingsByStatus(String status) {
        return bookingRepository.findByStatus(status);
    }

    /**
     * 根据用户ID和状态获取预订
     */
    public List<Booking> getBookingsByUserIdAndStatus(UUID userId, String status) {
        return bookingRepository.findByUserIdAndStatus(userId, status);
    }

    /**
     * 更新预订
     */
    public Booking updateBooking(UUID id, Booking updatedBooking) {
        Booking existingBooking = getBookingById(id);
        // 更新字段逻辑
        return bookingRepository.save(existingBooking);
    }

    /**
     * 取消预订
     */
    public Booking cancelBooking(UUID id) {
        Booking booking = getBookingById(id);
        booking.setStatus("CANCELLED");
        return bookingRepository.save(booking);
    }

    /**
     * 确认预订
     */
    public Booking confirmBooking(UUID id) {
        Booking booking = getBookingById(id);
        booking.setStatus("CONFIRMED");
        return bookingRepository.save(booking);
    }

    /**
     * 删除预订
     */
    public void deleteBooking(UUID id) {
        Booking booking = getBookingById(id);
        bookingRepository.delete(booking);
    }

    /**
     * 验证用户是否存在
     */
    private void validateUserExists(UUID userId) {
        try {
            userServiceClient.getUserById(userId);
        } catch (Exception e) {
            throw new IllegalArgumentException("User not found with id: " + userId);
        }
    }

    /**
     * 验证资源是否存在
     */
    private void validateResourceExists(String bookingType, UUID resourceId) {
        switch (bookingType.toUpperCase()) {
            case "HOTEL":
                try {
                    hotelServiceClient.getHotelById(resourceId);
                } catch (Exception e) {
                    throw new IllegalArgumentException("Hotel not found with id: " + resourceId);
                }
                break;
            case "FLIGHT":
                try {
                    flightServiceClient.getFlightById(resourceId);
                } catch (Exception e) {
                    throw new IllegalArgumentException("Flight not found with id: " + resourceId);
                }
                break;
            case "ATTRACTION":
                try {
                    attractionServiceClient.getAttractionById(resourceId);
                } catch (Exception e) {
                    throw new IllegalArgumentException("Attraction not found with id: " + resourceId);
                }
                break;
            default:
                throw new IllegalArgumentException("Unsupported booking type: " + bookingType);
        }
    }
}