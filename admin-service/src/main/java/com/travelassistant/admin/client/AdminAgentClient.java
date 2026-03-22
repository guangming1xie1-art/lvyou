package com.travelassistant.admin.client;

import com.travelassistant.admin.dto.RagDTOs;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;

@Component
@Slf4j
public class AdminAgentClient {

    private final WebClient webClient;
    private final String adminAgentUrl;
    private final int syncTimeout;

    public AdminAgentClient(
            WebClient.Builder webClientBuilder,
            @Value("${admin.agent.url:http://localhost:8091}") String adminAgentUrl,
            @Value("${admin.agent.sync.timeout:300}") int syncTimeout) {
        this.adminAgentUrl = adminAgentUrl;
        this.syncTimeout = syncTimeout;
        this.webClient = webClientBuilder
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(10 * 1024 * 1024))
                .build();
    }

    public Mono<RagDTOs.DocumentProcessResponse> processDocuments(RagDTOs.DocumentProcessRequest request) {
        log.info("Processing {} documents via admin-agent", request.getDocuments().size());

        return webClient.post()
                .uri(adminAgentUrl + "/api/v1/documents/process")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(RagDTOs.DocumentProcessResponse.class)
                .timeout(Duration.ofSeconds(syncTimeout))
                .doOnSuccess(response -> log.info("Successfully processed documents: {} chunks created", response.getChunkCount()))
                .doOnError(error -> log.error("Failed to process documents: {}", error.getMessage()));
    }

    public Mono<RagDTOs.SplitPreviewResponse> previewSplit(RagDTOs.SplitPreviewRequest request) {
        log.info("Previewing split for {} documents", request.getDocuments().size());

        return webClient.post()
                .uri(adminAgentUrl + "/api/v1/split/preview")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(RagDTOs.SplitPreviewResponse.class)
                .timeout(Duration.ofSeconds(60))
                .doOnError(error -> log.error("Failed to preview split: {}", error.getMessage()));
    }

    public Mono<RagDTOs.RagSyncStatusResponse> getStats() {
        return webClient.get()
                .uri(adminAgentUrl + "/api/v1/stats")
                .retrieve()
                .bodyToMono(RagDTOs.RagSyncStatusResponse.class)
                .timeout(Duration.ofSeconds(30));
    }

    public Mono<String> healthCheck() {
        return webClient.get()
                .uri(adminAgentUrl + "/api/v1/health")
                .retrieve()
                .bodyToMono(String.class)
                .timeout(Duration.ofSeconds(10));
    }
}
