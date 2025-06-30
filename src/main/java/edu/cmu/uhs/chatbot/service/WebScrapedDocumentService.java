package edu.cmu.uhs.chatbot.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.segment.TextSegment;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;

@Service
@Slf4j
@RequiredArgsConstructor
public class WebScrapedDocumentService {
    
    private final VectorStoreService vectorStoreService;
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    private static final int CHUNK_SIZE = 300;
    private static final int CHUNK_OVERLAP = 50;
    
    public Map<String, Object> ingestScrapedData(String scrapedDataPath) {
        Map<String, Object> result = new HashMap<>();
        int totalDocuments = 0;
        int successfullyIngested = 0;
        List<String> errors = new ArrayList<>();
        
        try {
            Path dataPath = Paths.get(scrapedDataPath);
            if (!Files.exists(dataPath)) {
                result.put("error", "Scraped data path does not exist: " + scrapedDataPath);
                return result;
            }
            
            // Process JSON files from scraper
            List<Path> jsonFiles = Files.walk(dataPath)
                .filter(path -> path.toString().endsWith("_processed.json"))
                .collect(Collectors.toList());
            
            for (Path jsonFile : jsonFiles) {
                try {
                    Map<String, Object> scrapedData = objectMapper.readValue(
                        jsonFile.toFile(), 
                        Map.class
                    );
                    
                    Document document = createDocumentFromScrapedData(scrapedData);
                    // Convert document to segments and add to vector store
                    List<TextSegment> segments = splitDocument(document);
                    vectorStoreService.addSegments(segments);
                    successfullyIngested++;
                    
                } catch (Exception e) {
                    errors.add("Failed to process " + jsonFile.getFileName() + ": " + e.getMessage());
                    log.error("Error processing scraped file: " + jsonFile, e);
                }
                totalDocuments++;
            }
            
            // Also process markdown exports if available
            Path markdownPath = dataPath.resolve("exports/markdown");
            if (Files.exists(markdownPath)) {
                List<Path> mdFiles = Files.walk(markdownPath)
                    .filter(path -> path.toString().endsWith(".md"))
                    .collect(Collectors.toList());
                
                for (Path mdFile : mdFiles) {
                    try {
                        String content = Files.readString(mdFile);
                        String url = extractUrlFromMarkdown(content);
                        
                        Document document = Document.from(
                            content,
                            Metadata.from(Map.of(
                                "source", "CMU Health Services Website",
                                "url", url != null ? url : "",
                                "title", mdFile.getFileName().toString().replace(".md", ""),
                                "type", "web_content",
                                "ingested_at", new Date().toString()
                            ))
                        );
                        
                        List<TextSegment> segments = splitDocument(document);
                        vectorStoreService.addSegments(segments);
                        successfullyIngested++;
                        
                    } catch (Exception e) {
                        errors.add("Failed to process " + mdFile.getFileName() + ": " + e.getMessage());
                        log.error("Error processing markdown file: " + mdFile, e);
                    }
                    totalDocuments++;
                }
            }
            
        } catch (IOException e) {
            log.error("Error reading scraped data", e);
            result.put("error", "Failed to read scraped data: " + e.getMessage());
            return result;
        }
        
        result.put("total_documents", totalDocuments);
        result.put("successfully_ingested", successfullyIngested);
        result.put("errors", errors);
        result.put("success", successfullyIngested > 0);
        
        log.info("Ingested {} out of {} scraped documents", successfullyIngested, totalDocuments);
        
        return result;
    }
    
    private Document createDocumentFromScrapedData(Map<String, Object> scrapedData) {
        String content = buildContentFromScrapedData(scrapedData);
        
        Metadata metadata = Metadata.from(Map.of(
            "source", "CMU Health Services Website",
            "url", scrapedData.getOrDefault("url", "").toString(),
            "title", scrapedData.getOrDefault("title", "").toString(),
            "category", scrapedData.getOrDefault("category", "general").toString(),
            "type", "web_content",
            "ingested_at", new Date().toString(),
            "scrape_date", scrapedData.getOrDefault("timestamp", "").toString()
        ));
        
        // Add extracted information if available
        Map<String, Object> extractedInfo = (Map<String, Object>) scrapedData.get("extracted_info");
        if (extractedInfo != null) {
            if (extractedInfo.containsKey("phone_numbers")) {
                metadata.put("phone_numbers", String.join(", ", 
                    (List<String>) extractedInfo.get("phone_numbers")));
            }
            if (extractedInfo.containsKey("emails")) {
                metadata.put("emails", String.join(", ", 
                    (List<String>) extractedInfo.get("emails")));
            }
            if (extractedInfo.containsKey("addresses")) {
                metadata.put("addresses", String.join("; ", 
                    (List<String>) extractedInfo.get("addresses")));
            }
        }
        
        return Document.from(content, metadata);
    }
    
    private String buildContentFromScrapedData(Map<String, Object> scrapedData) {
        StringBuilder content = new StringBuilder();
        
        // Add title
        String title = scrapedData.getOrDefault("title", "").toString();
        if (!title.isEmpty()) {
            content.append("# ").append(title).append("\n\n");
        }
        
        // Add URL for reference
        String url = scrapedData.getOrDefault("url", "").toString();
        if (!url.isEmpty()) {
            content.append("Source: ").append(url).append("\n\n");
        }
        
        // Add main content
        String mainContent = scrapedData.getOrDefault("content", "").toString();
        content.append(mainContent).append("\n\n");
        
        // Add processed content if different
        String processedContent = scrapedData.getOrDefault("processed_content", "").toString();
        if (!processedContent.isEmpty() && !processedContent.equals(mainContent)) {
            content.append("---\n\n").append(processedContent).append("\n\n");
        }
        
        // Add extracted Q&A pairs if available
        List<Map<String, String>> qaPairs = (List<Map<String, String>>) scrapedData.get("qa_pairs");
        if (qaPairs != null && !qaPairs.isEmpty()) {
            content.append("## Frequently Asked Questions\n\n");
            for (Map<String, String> qa : qaPairs) {
                content.append("**Q: ").append(qa.get("question")).append("**\n");
                content.append("A: ").append(qa.get("answer")).append("\n\n");
            }
        }
        
        return content.toString();
    }
    
    private String extractUrlFromMarkdown(String content) {
        String[] lines = content.split("\n");
        for (String line : lines) {
            if (line.startsWith("Source: ") || line.startsWith("URL: ")) {
                return line.substring(line.indexOf(": ") + 2).trim();
            }
        }
        return null;
    }
    
    private List<TextSegment> splitDocument(Document document) {
        var splitter = DocumentSplitters.recursive(CHUNK_SIZE, CHUNK_OVERLAP);
        return splitter.split(document);
    }
}