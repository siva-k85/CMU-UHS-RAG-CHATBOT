package edu.cmu.uhs.chatbot.service;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.DocumentParser;
import dev.langchain4j.data.document.parser.TextDocumentParser;
import dev.langchain4j.data.document.parser.apache.pdfbox.ApachePdfBoxDocumentParser;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.AllMiniLmL6V2EmbeddingModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingSearchResult;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

@Service
@Slf4j
public class VectorStoreService {
    
    protected EmbeddingModel embeddingModel;
    protected EmbeddingStore<TextSegment> embeddingStore;
    protected final AtomicInteger documentCount = new AtomicInteger(0);
    
    @PostConstruct
    public void init() {
        this.embeddingModel = new AllMiniLmL6V2EmbeddingModel();
        this.embeddingStore = new InMemoryEmbeddingStore<>();
        log.info("Vector store initialized with in-memory storage");
    }
    
    public void addSegments(List<TextSegment> segments) {
        for (TextSegment segment : segments) {
            Embedding embedding = embeddingModel.embed(segment).content();
            embeddingStore.add(embedding, segment);
        }
        log.info("Added {} segments to vector store", segments.size());
    }
    
    public void addDocument(MultipartFile file, String source) throws Exception {
        String filename = file.getOriginalFilename();
        DocumentParser parser;
        
        if (filename != null && filename.toLowerCase().endsWith(".pdf")) {
            parser = new ApachePdfBoxDocumentParser();
        } else {
            parser = new TextDocumentParser();
        }
        
        Document document = Document.from(new String(file.getBytes()));
        document.metadata().put("source", source);
        document.metadata().put("filename", filename);
        
        addDocumentToStore(document);
    }
    
    public void addDocumentFromText(String content, Map<String, Object> metadata) {
        Document document = Document.from(content);
        if (metadata != null) {
            metadata.forEach((key, value) -> {
                if (value != null) {
                    document.metadata().put(key, value.toString());
                }
            });
        }
        
        addDocumentToStore(document);
    }
    
    private void addDocumentToStore(Document document) {
        List<TextSegment> segments = DocumentSplitters.recursive(500, 50).split(document);
        
        addSegments(segments);
        documentCount.incrementAndGet();
    }
    
    public List<TextSegment> findRelevantSegments(String query, int maxResults) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        
        EmbeddingSearchRequest searchRequest = EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(maxResults)
                .minScore(0.5)
                .build();
        
        EmbeddingSearchResult<TextSegment> searchResult = embeddingStore.search(searchRequest);
        
        return searchResult.matches().stream()
                .map(EmbeddingMatch::embedded)
                .toList();
    }
    
    public void clearDocuments() {
        init();
        documentCount.set(0);
        log.info("Vector store cleared");
    }
    
    public int getDocumentCount() {
        return documentCount.get();
    }
}