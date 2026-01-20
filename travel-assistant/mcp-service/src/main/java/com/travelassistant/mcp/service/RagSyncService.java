package com.travelassistant.mcp.service;

import com.travelassistant.mcp.entity.Attraction;
import com.travelassistant.mcp.entity.Hotel;
import com.travelassistant.mcp.repository.AttractionRepository;
import com.travelassistant.mcp.repository.HotelRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class RagSyncService {
    private final HotelRepository hotelRepository;
    private final AttractionRepository attractionRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${agent.rag.sync.url:http://localhost:8000/api/rag/sync}")
    private String ragSyncUrl;

    @Scheduled(cron = "0 0 * * * *") // Every hour
    public void syncDataToRag() {
        log.info("Starting RAG data synchronization...");
        try {
            List<Map<String, Object>> documents = new ArrayList<>();

            List<Hotel> hotels = hotelRepository.findAll();
            for (Hotel hotel : hotels) {
                String content = String.format(
                    "酒店名称: %s\n所在地: %s\n价格: ¥%.0f/晚\n评分: %.1f/5.0\n设施: %s\n介绍: %s",
                    hotel.getName(), hotel.getDestination(), hotel.getPrice(), 
                    hotel.getRating(), hotel.getFacilities(), hotel.getDescription()
                );
                Map<String, Object> doc = new HashMap<>();
                doc.put("content", content);
                Map<String, Object> metadata = new HashMap<>();
                metadata.put("type", "hotel");
                metadata.put("id", hotel.getId());
                metadata.put("destination", hotel.getDestination());
                doc.put("metadata", metadata);
                documents.add(doc);
            }

            List<Attraction> attractions = attractionRepository.findAll();
            for (Attraction attraction : attractions) {
                String content = String.format(
                    "景点名称: %s\n所在地: %s\n类别: %s\n评分: %.1f/5.0\n开放时间: %s\n介绍: %s",
                    attraction.getName(), attraction.getDestination(), attraction.getCategory(),
                    attraction.getRating(), attraction.getOpeningHours(), attraction.getDescription()
                );
                Map<String, Object> doc = new HashMap<>();
                doc.put("content", content);
                Map<String, Object> metadata = new HashMap<>();
                metadata.put("type", "attraction");
                metadata.put("id", attraction.getId());
                metadata.put("destination", attraction.getDestination());
                doc.put("metadata", metadata);
                documents.add(doc);
            }

            if (!documents.isEmpty()) {
                Map<String, Object> request = new HashMap<>();
                request.put("documents", documents);
                restTemplate.postForObject(ragSyncUrl, request, Map.class);
                log.info("Successfully synced {} documents to RAG", documents.size());
            }
        } catch (Exception e) {
            log.error("Failed to sync data to RAG", e);
        }
    }
}
