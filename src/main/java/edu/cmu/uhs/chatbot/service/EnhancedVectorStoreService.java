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
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

@Service
@Primary
@Slf4j
@RequiredArgsConstructor
public class EnhancedVectorStoreService extends VectorStoreService {
    
    private final CacheService cacheService;
    
    @Value("${vector.search.min-score:0.6}")
    private double minScore;
    
    @Value("${vector.search.rerank:true}")
    private boolean enableReranking;
    
    @Value("${vector.chunk.size:600}")
    private int chunkSize;
    
    @Value("${vector.chunk.overlap:100}")
    private int chunkOverlap;
    
    // Track document metadata for better citation
    private final Map<String, DocumentMetadata> documentMetadataMap = new ConcurrentHashMap<>();
    
    // Track query patterns for optimization
    private final Map<String, QueryPattern> queryPatterns = new ConcurrentHashMap<>();
    
    @PostConstruct
    @Override
    public void init() {
        this.embeddingModel = new AllMiniLmL6V2EmbeddingModel();
        this.embeddingStore = new InMemoryEmbeddingStore<>();
        log.info("Enhanced vector store initialized with advanced features");
    }
    
    @Override
    public void addDocument(MultipartFile file, String source) throws Exception {
        String filename = file.getOriginalFilename();
        String documentId = UUID.randomUUID().toString();
        
        DocumentParser parser;
        if (filename != null && filename.toLowerCase().endsWith(".pdf")) {
            parser = new ApachePdfBoxDocumentParser();
        } else {
            parser = new TextDocumentParser();
        }
        
        Document document = Document.from(new String(file.getBytes()));
        
        // Enhanced metadata
        document.metadata().put("source", source);
        document.metadata().put("filename", filename);
        document.metadata().put("documentId", documentId);
        document.metadata().put("uploadTime", LocalDateTime.now().toString());
        document.metadata().put("fileSize", String.valueOf(file.getSize()));
        document.metadata().put("mimeType", file.getContentType());
        
        // Store document metadata
        DocumentMetadata metadata = new DocumentMetadata(
            documentId,
            filename,
            source,
            file.getSize(),
            LocalDateTime.now(),
            extractTitle(document.text())
        );
        documentMetadataMap.put(documentId, metadata);
        
        addDocumentToStore(document, documentId);
    }
    
    @Override
    public void addDocumentFromText(String content, Map<String, Object> metadata) {
        String documentId = metadata != null && metadata.containsKey("documentId") 
            ? metadata.get("documentId").toString() 
            : UUID.randomUUID().toString();
            
        Document document = Document.from(content);
        if (metadata != null) {
            metadata.forEach((key, value) -> {
                if (value != null) {
                    document.metadata().put(key, value.toString());
                }
            });
        }
        document.metadata().put("documentId", documentId);
        document.metadata().put("indexTime", LocalDateTime.now().toString());
        
        // Store document metadata
        DocumentMetadata docMeta = new DocumentMetadata(
            documentId,
            metadata != null ? metadata.getOrDefault("filename", "Unknown").toString() : "Unknown",
            metadata != null ? metadata.getOrDefault("source", "Manual").toString() : "Manual",
            content.length(),
            LocalDateTime.now(),
            extractTitle(content)
        );
        documentMetadataMap.put(documentId, docMeta);
        
        addDocumentToStore(document, documentId);
    }
    
    private void addDocumentToStore(Document document, String documentId) {
        // Use configurable chunk size and overlap
        List<TextSegment> segments = DocumentSplitters.recursive(chunkSize, chunkOverlap)
            .split(document);
        
        // Add chunk metadata
        for (int i = 0; i < segments.size(); i++) {
            TextSegment segment = segments.get(i);
            segment.metadata().put("chunkIndex", String.valueOf(i));
            segment.metadata().put("totalChunks", String.valueOf(segments.size()));
            segment.metadata().put("documentId", documentId);
        }
        
        addSegments(segments);
        documentCount.incrementAndGet();
        
        log.info("Added document {} with {} chunks to enhanced vector store", 
            documentId, segments.size());
    }
    
    @Override
    @Cacheable(value = "vectorSearch", key = "#query + '_' + #maxResults")
    public List<TextSegment> findRelevantSegments(String query, int maxResults) {
        // Track query pattern
        trackQueryPattern(query);
        
        // Check cache first
        String cacheKey = "vector_search_" + query.hashCode() + "_" + maxResults;
        List<TextSegment> cachedResult = cacheService.getCachedVectorSearch(cacheKey);
        if (cachedResult != null) {
            log.debug("Returning cached vector search results for query: {}", query);
            return cachedResult;
        }
        
        // Perform embedding search
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        
        EmbeddingSearchRequest searchRequest = EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(maxResults * 2) // Get more results for reranking
                .minScore(minScore)
                .build();
        
        EmbeddingSearchResult<TextSegment> searchResult = embeddingStore.search(searchRequest);
        
        List<ScoredSegment> scoredSegments = searchResult.matches().stream()
                .map(match -> new ScoredSegment(
                    match.embedded(),
                    match.score(),
                    calculateRelevanceScore(query, match.embedded())
                ))
                .collect(Collectors.toList());
        
        // Rerank if enabled
        if (enableReranking) {
            scoredSegments = rerankSegments(query, scoredSegments);
        }
        
        // Deduplicate and select top results
        List<TextSegment> results = deduplicateSegments(scoredSegments)
                .stream()
                .limit(maxResults)
                .map(ScoredSegment::segment)
                .collect(Collectors.toList());
        
        // Cache the results
        cacheService.cacheVectorSearch(cacheKey, results);
        
        return results;
    }
    
    private List<ScoredSegment> rerankSegments(String query, List<ScoredSegment> segments) {
        // Enhanced reranking based on multiple factors
        return segments.stream()
                .sorted((a, b) -> {
                    double scoreA = a.embeddingScore() * 0.6 + a.relevanceScore() * 0.4;
                    double scoreB = b.embeddingScore() * 0.6 + b.relevanceScore() * 0.4;
                    
                    // Boost recent documents
                    String timeA = a.segment().metadata().get("indexTime");
                    String timeB = b.segment().metadata().get("indexTime");
                    if (timeA != null && timeB != null) {
                        LocalDateTime dateA = LocalDateTime.parse(timeA);
                        LocalDateTime dateB = LocalDateTime.parse(timeB);
                        if (dateA.isAfter(dateB)) scoreA += 0.05;
                        else if (dateB.isAfter(dateA)) scoreB += 0.05;
                    }
                    
                    return Double.compare(scoreB, scoreA);
                })
                .collect(Collectors.toList());
    }
    
    private List<ScoredSegment> deduplicateSegments(List<ScoredSegment> segments) {
        Map<String, ScoredSegment> uniqueSegments = new LinkedHashMap<>();
        
        for (ScoredSegment segment : segments) {
            String docId = segment.segment().metadata().get("documentId");
            String chunkIndex = segment.segment().metadata().get("chunkIndex");
            String key = docId + "_" + chunkIndex;
            
            // Keep the highest scored version
            if (!uniqueSegments.containsKey(key) || 
                uniqueSegments.get(key).embeddingScore() < segment.embeddingScore()) {
                uniqueSegments.put(key, segment);
            }
        }
        
        return new ArrayList<>(uniqueSegments.values());
    }
    
    private double calculateRelevanceScore(String query, TextSegment segment) {
        String text = segment.text().toLowerCase();
        String[] queryTerms = query.toLowerCase().split("\\s+");
        
        double score = 0.0;
        int matchCount = 0;
        
        for (String term : queryTerms) {
            if (text.contains(term)) {
                matchCount++;
                // Boost exact matches
                if (text.contains(" " + term + " ")) {
                    score += 0.2;
                }
            }
        }
        
        // Term coverage score
        score += (double) matchCount / queryTerms.length;
        
        // Boost if segment contains health-related keywords
        if (text.contains("health") || text.contains("medical") || 
            text.contains("appointment") || text.contains("insurance")) {
            score += 0.1;
        }
        
        return Math.min(score, 1.0);
    }
    
    private void trackQueryPattern(String query) {
        String normalizedQuery = query.toLowerCase().trim();
        queryPatterns.compute(normalizedQuery, (k, v) -> {
            if (v == null) {
                return new QueryPattern(normalizedQuery, 1, LocalDateTime.now());
            } else {
                v.incrementCount();
                return v;
            }
        });
    }
    
    private String extractTitle(String content) {
        // Simple title extraction - take first line or first 100 chars
        String[] lines = content.split("\n");
        if (lines.length > 0 && !lines[0].trim().isEmpty()) {
            return lines[0].trim().substring(0, Math.min(lines[0].trim().length(), 100));
        }
        return content.substring(0, Math.min(content.length(), 100)) + "...";
    }
    
    public Map<String, DocumentMetadata> getDocumentMetadata() {
        return new HashMap<>(documentMetadataMap);
    }
    
    public Map<String, Integer> getQueryPatternStats() {
        return queryPatterns.entrySet().stream()
                .collect(Collectors.toMap(
                    Map.Entry::getKey,
                    e -> e.getValue().getCount()
                ));
    }
    
    @Override
    public void clearDocuments() {
        super.clearDocuments();
        documentMetadataMap.clear();
        queryPatterns.clear();
        cacheService.clearVectorSearchCache();
        log.info("Enhanced vector store cleared including metadata and cache");
    }
    
    // Inner classes
    private record ScoredSegment(TextSegment segment, double embeddingScore, double relevanceScore) {}
    
    private static class QueryPattern {
        private final String query;
        private int count;
        private LocalDateTime lastUsed;
        
        public QueryPattern(String query, int count, LocalDateTime lastUsed) {
            this.query = query;
            this.count = count;
            this.lastUsed = lastUsed;
        }
        
        public void incrementCount() {
            this.count++;
            this.lastUsed = LocalDateTime.now();
        }
        
        public int getCount() {
            return count;
        }
    }
    
    public record DocumentMetadata(
        String documentId,
        String filename,
        String source,
        long fileSize,
        LocalDateTime uploadTime,
        String title
    ) {}
}