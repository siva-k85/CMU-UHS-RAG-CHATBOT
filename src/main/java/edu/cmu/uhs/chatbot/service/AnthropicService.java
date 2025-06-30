package edu.cmu.uhs.chatbot.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
public class AnthropicService {
    
    private static final String ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages";
    private static final String CLAUDE_MODEL = "claude-3-haiku-20240307";
    
    @Value("${ANTHROPIC_API_KEY:${anthropic.api.key:demo}}")
    private String apiKey;
    
    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    public String generateResponse(String prompt) {
        if ("demo".equals(apiKey)) {
            return null; // Let the service handle demo mode
        }
        
        log.info("Using Anthropic API with key: {}...", apiKey.substring(0, Math.min(apiKey.length(), 10)));
        
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("x-api-key", apiKey.trim());
            headers.set("anthropic-version", "2023-06-01");
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", CLAUDE_MODEL);
            requestBody.put("max_tokens", 1000);
            requestBody.put("temperature", 0.7);
            requestBody.put("messages", List.of(
                Map.of(
                    "role", "user",
                    "content", prompt
                )
            ));
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                ANTHROPIC_API_URL,
                HttpMethod.POST,
                request,
                Map.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                Map<String, Object> responseBody = response.getBody();
                List<Map<String, Object>> content = (List<Map<String, Object>>) responseBody.get("content");
                if (content != null && !content.isEmpty()) {
                    return (String) content.get(0).get("text");
                }
            }
            
            return "Unable to generate response from Claude.";
            
        } catch (Exception e) {
            log.error("Error calling Anthropic API", e);
            throw new RuntimeException("Failed to call Anthropic API: " + e.getMessage());
        }
    }
}