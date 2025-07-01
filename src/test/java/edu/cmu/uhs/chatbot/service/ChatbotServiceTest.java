package edu.cmu.uhs.chatbot.service;

import dev.langchain4j.data.segment.TextSegment;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ChatbotServiceTest {

    @Mock
    private VectorStoreService vectorStoreService;

    @InjectMocks
    private ChatbotService chatbotService;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(chatbotService, "openAiApiKey", "test-api-key");
    }

    @Test
    void testChatWithRelevantSegments() {
        String userMessage = "What are the health services hours?";
        TextSegment segment = TextSegment.from("CMU UHS hours are Monday-Friday 8:30 AM - 5:00 PM");
        
        when(vectorStoreService.findRelevantSegments(anyString(), anyInt()))
                .thenReturn(List.of(segment));

        String response = chatbotService.chat(userMessage);

        assertNotNull(response);
        verify(vectorStoreService).findRelevantSegments(userMessage, 5);
    }

    @Test
    void testChatWithNoRelevantSegments() {
        String userMessage = "Random unrelated question";
        
        when(vectorStoreService.findRelevantSegments(anyString(), anyInt()))
                .thenReturn(Collections.emptyList());

        String response = chatbotService.chat(userMessage);

        assertNotNull(response);
        verify(vectorStoreService).findRelevantSegments(userMessage, 5);
    }

    @Test
    void testChatInDemoMode() {
        ReflectionTestUtils.setField(chatbotService, "openAiApiKey", "demo");
        String userMessage = "What services do you offer?";

        when(vectorStoreService.findRelevantSegments(anyString(), anyInt()))
                .thenReturn(Collections.emptyList());

        String response = chatbotService.chat(userMessage);

        assertNotNull(response);
        assertTrue(response.contains("demo mode"));
        assertTrue(response.contains("CMU UHS"));
    }

    @Test
    void testChatWithMultipleSegments() {
        String userMessage = "Tell me about appointments and insurance";
        List<TextSegment> segments = Arrays.asList(
                TextSegment.from("Appointments can be scheduled online or by phone"),
                TextSegment.from("Insurance is required for all students"),
                TextSegment.from("Walk-in appointments are available for urgent care")
        );

        when(vectorStoreService.findRelevantSegments(anyString(), anyInt()))
                .thenReturn(segments);

        String response = chatbotService.chat(userMessage);

        assertNotNull(response);
        verify(vectorStoreService).findRelevantSegments(userMessage, 5);
    }

    @Test
    void testChatWithException() {
        String userMessage = "Test message";
        
        when(vectorStoreService.findRelevantSegments(anyString(), anyInt()))
                .thenThrow(new RuntimeException("Vector store error"));

        String response = chatbotService.chat(userMessage);

        assertNotNull(response);
        assertTrue(response.contains("error") || response.contains("apologize"));
    }

    @Test
    void testBuildContextWithSegments() {
        List<TextSegment> segments = Arrays.asList(
                TextSegment.from("First segment content"),
                TextSegment.from("Second segment content")
        );

        when(vectorStoreService.findRelevantSegments(anyString(), anyInt()))
                .thenReturn(segments);

        String response = chatbotService.chat("test");

        assertNotNull(response);
    }

    @Test
    void testChatWithEmptyMessage() {
        String response = chatbotService.chat("");

        assertNotNull(response);
        verify(vectorStoreService).findRelevantSegments("", 5);
    }

    @Test
    void testChatWithLongMessage() {
        String longMessage = "This is a very long message ".repeat(50);
        
        when(vectorStoreService.findRelevantSegments(anyString(), anyInt()))
                .thenReturn(Collections.emptyList());

        String response = chatbotService.chat(longMessage);

        assertNotNull(response);
        verify(vectorStoreService).findRelevantSegments(longMessage, 5);
    }

    @Test
    void testChatWithSpecialCharacters() {
        String messageWithSpecialChars = "What about COVID-19 testing? Is it @vailable 24/7?";
        
        when(vectorStoreService.findRelevantSegments(anyString(), anyInt()))
                .thenReturn(Collections.emptyList());

        String response = chatbotService.chat(messageWithSpecialChars);

        assertNotNull(response);
    }
}