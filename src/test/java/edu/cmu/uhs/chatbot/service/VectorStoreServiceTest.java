package edu.cmu.uhs.chatbot.service;

import dev.langchain4j.data.segment.TextSegment;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class VectorStoreServiceTest {

    @InjectMocks
    private VectorStoreService vectorStoreService;

    @BeforeEach
    void setUp() {
        vectorStoreService.init();
    }

    @Test
    void testAddSegments() {
        TextSegment segment1 = TextSegment.from("This is a test segment about CMU Health Services.");
        TextSegment segment2 = TextSegment.from("CMU UHS provides comprehensive healthcare to students.");
        List<TextSegment> segments = List.of(segment1, segment2);

        vectorStoreService.addSegments(segments);

        assertEquals(1, vectorStoreService.getDocumentCount());
    }

    @Test
    void testAddDocumentFromText() {
        String content = "CMU University Health Services is located at 1060 Morewood Avenue.";
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("source", "test");
        metadata.put("type", "location");

        vectorStoreService.addDocumentFromText(content, metadata);

        assertEquals(1, vectorStoreService.getDocumentCount());
    }

    @Test
    void testFindRelevantSegments() {
        String content1 = "CMU Health Services offers appointments for students.";
        String content2 = "The library is open 24/7 during finals week.";
        String content3 = "Health insurance is required for all CMU students.";

        vectorStoreService.addDocumentFromText(content1, null);
        vectorStoreService.addDocumentFromText(content2, null);
        vectorStoreService.addDocumentFromText(content3, null);

        List<TextSegment> relevantSegments = vectorStoreService.findRelevantSegments("health services", 2);

        assertNotNull(relevantSegments);
        assertFalse(relevantSegments.isEmpty());
        assertTrue(relevantSegments.size() <= 2);
    }

    @Test
    void testAddDocumentPDF() throws Exception {
        String pdfContent = "Sample PDF content about health services";
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "test.pdf",
                "application/pdf",
                pdfContent.getBytes()
        );

        vectorStoreService.addDocument(file, "test-source");

        assertEquals(1, vectorStoreService.getDocumentCount());
    }

    @Test
    void testAddDocumentText() throws Exception {
        String textContent = "Sample text content about appointments";
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "test.txt",
                "text/plain",
                textContent.getBytes()
        );

        vectorStoreService.addDocument(file, "test-source");

        assertEquals(1, vectorStoreService.getDocumentCount());
    }

    @Test
    void testClearDocuments() {
        vectorStoreService.addDocumentFromText("Test content", null);
        assertEquals(1, vectorStoreService.getDocumentCount());

        vectorStoreService.clearDocuments();

        assertEquals(0, vectorStoreService.getDocumentCount());
    }

    @Test
    void testFindRelevantSegmentsWithMinScore() {
        String content = "Emergency services are available 24/7 at CMU.";
        vectorStoreService.addDocumentFromText(content, null);

        List<TextSegment> relevantSegments = vectorStoreService.findRelevantSegments("unrelated query about food", 5);

        assertTrue(relevantSegments.isEmpty() || relevantSegments.size() < 5);
    }

    @Test
    void testMetadataPreservation() {
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("source", "official-docs");
        metadata.put("category", "health");
        metadata.put("lastUpdated", "2024-01-01");

        String content = "CMU Health Services provides mental health counseling.";
        vectorStoreService.addDocumentFromText(content, metadata);

        List<TextSegment> segments = vectorStoreService.findRelevantSegments("mental health", 1);

        assertFalse(segments.isEmpty());
        TextSegment segment = segments.get(0);
        assertEquals("official-docs", segment.metadata().get("source"));
        assertEquals("health", segment.metadata().get("category"));
    }

    @Test
    void testEmptyQuery() {
        vectorStoreService.addDocumentFromText("Test content", null);

        List<TextSegment> relevantSegments = vectorStoreService.findRelevantSegments("", 5);

        assertNotNull(relevantSegments);
    }

    @Test
    void testLargeDocument() {
        StringBuilder largeContent = new StringBuilder();
        for (int i = 0; i < 100; i++) {
            largeContent.append("This is paragraph ").append(i)
                    .append(" about CMU Health Services and various medical topics. ");
        }

        vectorStoreService.addDocumentFromText(largeContent.toString(), null);

        assertEquals(1, vectorStoreService.getDocumentCount());
        
        List<TextSegment> segments = vectorStoreService.findRelevantSegments("paragraph 50", 1);
        assertFalse(segments.isEmpty());
    }
}