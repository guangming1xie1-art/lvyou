package com.travelassistant.mcp.service;

import com.travelassistant.mcp.dto.SearchAttractionRequest;
import com.travelassistant.mcp.dto.SearchFlightRequest;
import com.travelassistant.mcp.dto.SearchHotelRequest;
import com.travelassistant.mcp.entity.Attraction;
import com.travelassistant.mcp.entity.Flight;
import com.travelassistant.mcp.entity.Hotel;
import com.travelassistant.mcp.repository.AttractionRepository;
import com.travelassistant.mcp.repository.FlightRepository;
import com.travelassistant.mcp.repository.HotelRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class SearchService {
    private final HotelRepository hotelRepository;
    private final FlightRepository flightRepository;
    private final AttractionRepository attractionRepository;

    public List<Hotel> searchHotels(SearchHotelRequest request) {
        return hotelRepository.searchHotels(
            request.getDestination(),
            request.getPriceMin(),
            request.getPriceMax(),
            request.getRatingMin()
        );
    }

    public List<Flight> searchFlights(SearchFlightRequest request) {
        return flightRepository.findByOriginAndDestination(
            request.getOrigin(),
            request.getDestination()
        );
    }

    public List<Attraction> searchAttractions(SearchAttractionRequest request) {
        return attractionRepository.findByDestination(request.getDestination());
    }
}
