package com.travelassistant.mcp;

import com.travelassistant.mcp.dto.SearchHotelRequest;
import com.travelassistant.mcp.entity.Hotel;
import com.travelassistant.mcp.repository.HotelRepository;
import com.travelassistant.mcp.service.SearchService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.util.Collections;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class SearchServiceTest {
    @Mock
    private HotelRepository hotelRepository;

    @InjectMocks
    private SearchService searchService;

    @Test
    public void testSearchHotels() {
        SearchHotelRequest request = new SearchHotelRequest();
        request.setDestination("Hangzhou");
        
        Hotel hotel = new Hotel();
        hotel.setName("West Lake Hotel");
        
        when(hotelRepository.searchHotels(anyString(), anyDouble(), anyDouble(), anyDouble()))
            .thenReturn(Collections.singletonList(hotel));
            
        List<Hotel> results = searchService.searchHotels(request);
        
        assertEquals(1, results.size());
        assertEquals("West Lake Hotel", results.get(0).getName());
    }
}
