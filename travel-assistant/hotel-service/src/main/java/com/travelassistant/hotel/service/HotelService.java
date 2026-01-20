package com.travelassistant.hotel.service;

import com.travelassistant.hotel.entity.Hotel;
import com.travelassistant.hotel.repository.HotelRepository;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@Service
@Transactional
public class HotelService {

    @Autowired
    private HotelRepository hotelRepository;

    /**
     * 创建酒店
     */
    public Hotel createHotel(Hotel hotel) {
        return hotelRepository.save(hotel);
    }

    /**
     * 根据ID获取酒店
     */
    public Hotel getHotelById(UUID id) {
        return hotelRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Hotel not found with id: " + id));
    }

    /**
     * 获取所有酒店
     */
    public List<Hotel> getAllHotels() {
        return hotelRepository.findAll();
    }

    /**
     * 根据目的地获取酒店
     */
    public List<Hotel> getHotelsByDestination(String destination) {
        return hotelRepository.findByDestination(destination);
    }

    /**
     * 根据价格范围获取酒店
     */
    public List<Hotel> getHotelsByPriceRange(BigDecimal minPrice, BigDecimal maxPrice) {
        return hotelRepository.findByPriceRange(minPrice, maxPrice);
    }

    /**
     * 根据评分获取酒店
     */
    public List<Hotel> getHotelsByMinRating(BigDecimal minRating) {
        return hotelRepository.findByMinRating(minRating);
    }

    /**
     * 根据目的地和价格范围获取酒店
     */
    public List<Hotel> getHotelsByDestinationAndPriceRange(String destination, BigDecimal minPrice, BigDecimal maxPrice) {
        return hotelRepository.findByDestinationAndPriceRange(destination, minPrice, maxPrice);
    }

    /**
     * 根据设施获取酒店
     */
    public List<Hotel> getHotelsByFacility(String facility) {
        return hotelRepository.findByFacility(facility);
    }

    /**
     * 更新酒店
     */
    public Hotel updateHotel(UUID id, Hotel updatedHotel) {
        Hotel existingHotel = getHotelById(id);
        // 更新字段逻辑
        return hotelRepository.save(existingHotel);
    }

    /**
     * 删除酒店
     */
    public void deleteHotel(UUID id) {
        Hotel hotel = getHotelById(id);
        hotelRepository.delete(hotel);
    }
}