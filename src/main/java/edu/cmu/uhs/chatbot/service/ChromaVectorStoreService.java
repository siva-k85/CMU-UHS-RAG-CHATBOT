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
import dev.langchain4j.store.embedding.chroma.ChromaEmbeddingStore;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

@Service
@Profile("!test")
@Slf4j
public class ChromaVectorStoreService extends VectorStoreService {
    
    @Value("${chroma.url:http://localhost:8000}")
    private String chromaUrl;
    
    @Value("${chroma.collection:cmu-uhs-docs}")
    private String collectionName;
    
    @PostConstruct
    @Override
    public void init() {
        this.embeddingModel = new AllMiniLmL6V2EmbeddingModel();
        
        try {
            this.embeddingStore = ChromaEmbeddingStore.builder()
                    .baseUrl(chromaUrl)
                    .collectionName(collectionName)
                    .build();
            log.info("Vector store initialized with Chroma at {} using collection '{}'", chromaUrl, collectionName);
        } catch (Exception e) {
            log.warn("Failed to connect to Chroma, falling back to in-memory store", e);
            super.init(); // Fall back to in-memory store
        }
    }
    
    public boolean isConnected() {
        try {
            // Test connection by performing a simple search
            findRelevantSegments("test", 1);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}