package com.travelassistant.mcp;

import com.travelassistant.mcp.controller.McpProtocolController;
import com.travelassistant.mcp.dto.SearchHotelRequest;
import com.travelassistant.mcp.service.RecommendService;
import com.travelassistant.mcp.service.SearchService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import java.util.Collections;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(McpProtocolController.class)
public class McpControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private SearchService searchService;

    @MockBean
    private RecommendService recommendService;

    @Test
    public void testSearchHotelsEndpoint() throws Exception {
        when(searchService.searchHotels(any(SearchHotelRequest.class)))
            .thenReturn(Collections.emptyList());

        mockMvc.perform(post("/mcp/search-hotels")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"destination\":\"Hangzhou\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.message").value("success"));
    }
}
