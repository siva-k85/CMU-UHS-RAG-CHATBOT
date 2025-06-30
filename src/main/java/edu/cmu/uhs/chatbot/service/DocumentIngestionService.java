package edu.cmu.uhs.chatbot.service;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.DocumentParser;
import dev.langchain4j.data.document.DocumentSplitter;
import dev.langchain4j.data.document.parser.apache.pdfbox.ApachePdfBoxDocumentParser;
import dev.langchain4j.data.document.parser.TextDocumentParser;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.segment.TextSegment;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

@Service
@Slf4j
@RequiredArgsConstructor
public class DocumentIngestionService {
    
    private final VectorStoreService vectorStoreService;
    
    private static final int CHUNK_SIZE = 300;
    private static final int CHUNK_OVERLAP = 50;
    
    public void ingestDocument(MultipartFile file) throws IOException {
        String fileName = file.getOriginalFilename();
        log.info("Ingesting document: {}", fileName);
        
        Document document;
        try (InputStream inputStream = file.getInputStream()) {
            DocumentParser parser = getParser(fileName);
            document = parser.parse(inputStream);
        }
        
        List<TextSegment> segments = splitDocument(document);
        vectorStoreService.addSegments(segments);
        
        log.info("Successfully ingested {} segments from {}", segments.size(), fileName);
    }
    
    public void ingestDirectory(String directoryPath) throws IOException {
        Path dir = Paths.get(directoryPath);
        if (!Files.exists(dir) || !Files.isDirectory(dir)) {
            throw new IllegalArgumentException("Invalid directory path: " + directoryPath);
        }
        
        List<TextSegment> allSegments = new ArrayList<>();
        
        Files.walk(dir)
            .filter(Files::isRegularFile)
            .filter(path -> isSupportedFile(path.toString()))
            .forEach(path -> {
                try {
                    log.info("Processing file: {}", path);
                    Document document = loadDocument(path);
                    List<TextSegment> segments = splitDocument(document);
                    allSegments.addAll(segments);
                } catch (Exception e) {
                    log.error("Error processing file: {}", path, e);
                }
            });
        
        vectorStoreService.addSegments(allSegments);
        log.info("Successfully ingested {} total segments from directory", allSegments.size());
    }
    
    private Document loadDocument(Path filePath) throws IOException {
        DocumentParser parser = getParser(filePath.toString());
        try (InputStream inputStream = Files.newInputStream(filePath)) {
            return parser.parse(inputStream);
        }
    }
    
    private List<TextSegment> splitDocument(Document document) {
        DocumentSplitter splitter = DocumentSplitters.recursive(CHUNK_SIZE, CHUNK_OVERLAP);
        return splitter.split(document);
    }
    
    private DocumentParser getParser(String fileName) {
        if (fileName.toLowerCase().endsWith(".pdf")) {
            return new ApachePdfBoxDocumentParser();
        } else if (fileName.toLowerCase().endsWith(".txt") || 
                   fileName.toLowerCase().endsWith(".md")) {
            return new TextDocumentParser();
        } else {
            throw new UnsupportedOperationException("Unsupported file type: " + fileName);
        }
    }
    
    private boolean isSupportedFile(String fileName) {
        String lowerCase = fileName.toLowerCase();
        return lowerCase.endsWith(".pdf") || 
               lowerCase.endsWith(".txt") || 
               lowerCase.endsWith(".md");
    }
}