package edu.cmu.uhs.chatbot.controller;

import edu.cmu.uhs.chatbot.model.ChatRequest;
import edu.cmu.uhs.chatbot.model.ChatMetric;
import edu.cmu.uhs.chatbot.service.EnhancedChatbotService;
import edu.cmu.uhs.chatbot.service.WebScrapedDocumentService;
import edu.cmu.uhs.chatbot.service.MetricsService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.List;
import java.util.UUID;
import jakarta.servlet.http.HttpSession;

@RestController
@RequestMapping("/api/v2")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
@Slf4j
public class EnhancedChatController {
    
    private final EnhancedChatbotService enhancedChatbotService;
    private final WebScrapedDocumentService webScrapedDocumentService;
    private final MetricsService metricsService;
    
    @PostMapping("/chat")
    public ResponseEntity<Map<String, Object>> chatWithCitations(@RequestBody ChatRequest request, HttpSession session) {
        log.info("Enhanced chat request received: {}", request.getMessage());
        
        // Start timing
        long startTime = System.currentTimeMillis();
        
        // Get or create session ID
        String sessionId = (String) session.getAttribute("sessionId");
        if (sessionId == null) {
            sessionId = UUID.randomUUID().toString();
            session.setAttribute("sessionId", sessionId);
        }
        
        // Process chat request
        Map<String, Object> response = enhancedChatbotService.chatWithCitations(request.getMessage());
        
        // Calculate response time
        long responseTime = System.currentTimeMillis() - startTime;
        
        // Create metric
        ChatMetric metric = ChatMetric.builder()
            .sessionId(sessionId)
            .query(request.getMessage())
            .response(response.get("response").toString())
            .timestamp(LocalDateTime.now())
            .responseTimeMs(responseTime)
            .queryLength(request.getMessage().length())
            .responseLength(response.get("response").toString().length())
            .citationsCount(((List<?>) response.getOrDefault("citations", List.of())).size())
            .relevantDocsCount((Integer) response.getOrDefault("sources_used", 0))
            .llmProvider("anthropic")
            .wasSuccessful(!response.containsKey("error"))
            .errorType(response.containsKey("error") ? response.get("error").toString() : null)
            .build();
        
        // Record metric
        metricsService.recordMetric(metric);
        
        // Add session info to response
        response.put("sessionId", sessionId);
        
        return ResponseEntity.ok(response);
    }
    
    @PostMapping("/ingest/scraped-data")
    public ResponseEntity<Map<String, Object>> ingestScrapedData(@RequestBody Map<String, String> request) {
        String dataPath = request.getOrDefault("path", "scraped_data");
        log.info("Ingesting scraped data from: {}", dataPath);
        
        Map<String, Object> result = webScrapedDocumentService.ingestScrapedData(dataPath);
        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
            "status", "healthy",
            "service", "CMU UHS Enhanced RAG Chatbot with Citations",
            "version", "2.0"
        ));
    }
}