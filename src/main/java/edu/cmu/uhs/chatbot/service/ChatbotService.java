package edu.cmu.uhs.chatbot.service;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@Slf4j
@RequiredArgsConstructor
public class ChatbotService {
    
    private final VectorStoreService vectorStoreService;
    
    @Value("${OPENAI_API_KEY:${openai.api.key:demo}}")
    private String openAiApiKey;
    
    private static final int MAX_RELEVANT_DOCUMENTS = 5;
    
    public String chat(String userMessage) {
        log.info("Processing user message: {}", userMessage);
        log.info("Using OpenAI API key: {}", openAiApiKey.substring(0, 10) + "...");
        
        try {
            List<TextSegment> relevantSegments = vectorStoreService.findRelevantSegments(
                userMessage, MAX_RELEVANT_DOCUMENTS
            );
            
            String context = buildContext(relevantSegments);
            String prompt = buildPrompt(userMessage, context);
            
            if ("demo".equals(openAiApiKey)) {
                return "The chatbot is running in demo mode. Please set your OpenAI API key to enable full functionality. " +
                       "Based on the knowledge base: CMU UHS is located at 1060 Morewood Avenue, Pittsburgh, PA 15213. " +
                       "Hours: Monday-Friday 8:30 AM - 5:00 PM. Phone: 412-268-2157.";
            }
            
            ChatLanguageModel chatModel = OpenAiChatModel.builder()
                    .apiKey(openAiApiKey)
                    .modelName("gpt-3.5-turbo")
                    .temperature(0.7)
                    .build();
            
            String response = chatModel.generate(prompt);
            log.info("Generated response for user query");
            
            return response;
        } catch (Exception e) {
            log.error("Error processing chat request", e);
            
            // Provide a demo response based on the knowledge base
            if (userMessage.toLowerCase().contains("hours")) {
                return "Based on our knowledge base: CMU University Health Services is open Monday-Friday 8:30 AM - 5:00 PM. " +
                       "For after-hours care, a 24/7 nurse advice line is available. For emergencies, call 911.";
            } else if (userMessage.toLowerCase().contains("location") || userMessage.toLowerCase().contains("address")) {
                return "CMU University Health Services is located at 1060 Morewood Avenue, Pittsburgh, PA 15213. " +
                       "You can reach them at 412-268-2157.";
            } else if (userMessage.toLowerCase().contains("service")) {
                return "CMU UHS offers: Primary Care, Mental Health Services, Immunizations, Laboratory Services, " +
                       "Pharmacy, Health Education Programs, and specialized services for international students, " +
                       "women's health, and LGBTQ+ health. Call 412-268-2157 for more information.";
            } else {
                return "I apologize, the AI service is temporarily unavailable. However, based on our knowledge base, " +
                       "CMU UHS can be reached at 412-268-2157. They are located at 1060 Morewood Avenue and are " +
                       "open Monday-Friday 8:30 AM - 5:00 PM.";
            }
        }
    }
    
    private String buildContext(List<TextSegment> segments) {
        if (segments.isEmpty()) {
            return "No relevant information found in the knowledge base.";
        }
        
        return segments.stream()
                .map(TextSegment::text)
                .collect(Collectors.joining("\n\n"));
    }
    
    private String buildPrompt(String userMessage, String context) {
        return String.format("""
            You are a helpful assistant for Carnegie Mellon University Health Services (CMU UHS).
            Your role is to provide accurate information about health services, appointments, and general health guidance
            based on the CMU UHS knowledge base.
            
            Context from CMU UHS documents:
            %s
            
            User Question: %s
            
            Please provide a helpful and accurate response based on the context provided.
            If the information is not available in the context, politely indicate that and suggest
            contacting CMU UHS directly at 412-268-2157 or visiting their website.
            
            Response:""", context, userMessage);
    }
}