package edu.cmu.uhs.chatbot.service;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
@Slf4j
@RequiredArgsConstructor
public class EnhancedChatbotService {
    
    private final VectorStoreService vectorStoreService;
    private final AnthropicService anthropicService;
    
    @Value("${ANTHROPIC_API_KEY:${anthropic.api.key:demo}}")
    private String anthropicApiKey;
    
    @Value("${LLM_PROVIDER:anthropic}")
    private String llmProvider;
    
    private static final int MAX_RELEVANT_DOCUMENTS = 5;
    
    public Map<String, Object> chatWithCitations(String userMessage) {
        log.info("Processing user message with citations: {}", userMessage);
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            // Find relevant segments with metadata
            List<TextSegment> relevantSegments = vectorStoreService.findRelevantSegments(
                userMessage, MAX_RELEVANT_DOCUMENTS
            );
            
            // Extract citations from metadata
            List<Map<String, String>> citations = extractCitations(relevantSegments);
            
            // Build context with source information
            String contextWithSources = buildContextWithSources(relevantSegments);
            String prompt = buildEnhancedPrompt(userMessage, contextWithSources);
            
            if ("demo".equals(anthropicApiKey)) {
                // In demo mode, provide a response based on the context
                String demoResponse = generateDemoResponse(userMessage, relevantSegments);
                response.put("response", demoResponse);
                response.put("citations", citations);
                response.put("demo_mode", true);
                return response;
            }
            
            String aiResponse;
            
            if ("anthropic".equalsIgnoreCase(llmProvider)) {
                // Use custom Anthropic service
                aiResponse = anthropicService.generateResponse(prompt);
                if (aiResponse == null) {
                    // Handle demo mode or error
                    aiResponse = generateDemoResponse(userMessage, relevantSegments);
                    response.put("demo_mode", true);
                }
            } else {
                // Fallback to OpenAI if needed
                ChatLanguageModel chatModel = OpenAiChatModel.builder()
                        .apiKey(anthropicApiKey) // Would need to change this to openAiApiKey if using OpenAI
                        .modelName("gpt-3.5-turbo")
                        .temperature(0.7)
                        .build();
                aiResponse = chatModel.generate(prompt);
            }
            
            response.put("response", aiResponse);
            response.put("citations", citations);
            response.put("sources_used", relevantSegments.size());
            
            log.info("Generated response with {} citations", citations.size());
            return response;
            
        } catch (Exception e) {
            log.error("Error processing chat with citations", e);
            response.put("response", "I encountered an error processing your request. Please try again.");
            response.put("citations", new ArrayList<>());
            response.put("error", e.getMessage());
            return response;
        }
    }
    
    private List<Map<String, String>> extractCitations(List<TextSegment> segments) {
        return segments.stream()
            .map(segment -> {
                Map<String, String> citation = new HashMap<>();
                var metadata = segment.metadata().toMap();
                
                citation.put("source", metadata.getOrDefault("source", "Unknown").toString());
                citation.put("title", metadata.getOrDefault("title", "CMU Health Services").toString());
                citation.put("url", metadata.getOrDefault("url", "").toString());
                citation.put("snippet", segment.text().substring(0, Math.min(segment.text().length(), 200)) + "...");
                
                return citation;
            })
            .collect(Collectors.toList());
    }
    
    private String buildContextWithSources(List<TextSegment> relevantSegments) {
        if (relevantSegments.isEmpty()) {
            return "No specific information found in the knowledge base.";
        }
        
        StringBuilder context = new StringBuilder();
        for (int i = 0; i < relevantSegments.size(); i++) {
            TextSegment segment = relevantSegments.get(i);
            var metadata = segment.metadata().toMap();
            
            context.append("Source ").append(i + 1).append(" (")
                   .append(metadata.getOrDefault("title", "CMU Health Services"))
                   .append("): ");
            context.append(segment.text()).append("\n\n");
        }
        
        return context.toString();
    }
    
    private String buildEnhancedPrompt(String userMessage, String context) {
        return String.format(
            """
            You are a helpful AI assistant for Carnegie Mellon University Health Services.
            
            Context from CMU Health Services documentation:
            %s
            
            User Question: %s
            
            Instructions:
            1. Answer based ONLY on the provided context
            2. If the context doesn't contain enough information, say so
            3. Be specific and mention relevant details like hours, locations, phone numbers
            4. When citing information, reference it naturally (e.g., "According to the CMU Health Services website...")
            5. Keep the response concise and student-friendly
            
            Response:
            """, context, userMessage);
    }
    
    private String generateDemoResponse(String userMessage, List<TextSegment> relevantSegments) {
        if (relevantSegments.isEmpty()) {
            return "I couldn't find specific information about your query in my knowledge base. Please try rephrasing your question or contact CMU Health Services directly at 412-268-2157.";
        }
        
        // Create a simple response based on the most relevant segment
        StringBuilder response = new StringBuilder();
        response.append("Based on the CMU Health Services information I have:\n\n");
        
        // Add content from the most relevant segment
        TextSegment topSegment = relevantSegments.get(0);
        String content = topSegment.text();
        
        // Limit response length
        if (content.length() > 500) {
            content = content.substring(0, 500) + "...";
        }
        
        response.append(content);
        
        // Add a note about demo mode
        response.append("\n\n[Note: Running in demo mode. For more detailed responses, please configure an OpenAI API key.]");
        
        return response.toString();
    }
}