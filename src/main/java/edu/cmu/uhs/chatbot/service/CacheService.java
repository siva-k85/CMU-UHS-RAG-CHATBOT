package edu.cmu.uhs.chatbot.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.CachePut;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
@RequiredArgsConstructor
@Slf4j
public class CacheService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final Map<String, Long> cacheStats = new ConcurrentHashMap<>();

    @Cacheable(value = "chatResponses", key = "#query", unless = "#result == null")
    public String getCachedResponse(String query) {
        log.debug("Cache miss for query: {}", query);
        return null;
    }

    @CachePut(value = "chatResponses", key = "#query")
    public String cacheResponse(String query, String response) {
        log.debug("Caching response for query: {}", query);
        updateCacheStats("chatResponses");
        return response;
    }

    @Cacheable(value = "embeddings", key = "#text.hashCode()", unless = "#result == null")
    public List<Float> getCachedEmbedding(String text) {
        log.debug("Cache miss for embedding text: {}", text.substring(0, Math.min(text.length(), 50)) + "...");
        return null;
    }

    @CachePut(value = "embeddings", key = "#text.hashCode()")
    public List<Float> cacheEmbedding(String text, List<Float> embedding) {
        log.debug("Caching embedding for text: {}", text.substring(0, Math.min(text.length(), 50)) + "...");
        updateCacheStats("embeddings");
        return embedding;
    }

    @Cacheable(value = "documentSegments", key = "#documentId", unless = "#result == null")
    public List<String> getCachedDocumentSegments(String documentId) {
        return null;
    }

    @CachePut(value = "documentSegments", key = "#documentId")
    public List<String> cacheDocumentSegments(String documentId, List<String> segments) {
        updateCacheStats("documentSegments");
        return segments;
    }

    @CacheEvict(value = "chatResponses", allEntries = true)
    public void clearChatCache() {
        log.info("Clearing chat response cache");
    }

    @CacheEvict(value = "embeddings", allEntries = true)
    public void clearEmbeddingCache() {
        log.info("Clearing embedding cache");
    }

    @CacheEvict(value = {"chatResponses", "embeddings", "documentSegments"}, allEntries = true)
    public void clearAllCaches() {
        log.info("Clearing all caches");
        cacheStats.clear();
    }

    public void setCacheWithTTL(String key, Object value, Duration ttl) {
        redisTemplate.opsForValue().set(key, value, ttl);
    }

    public Object getFromCache(String key) {
        return redisTemplate.opsForValue().get(key);
    }

    public void removeFromCache(String key) {
        redisTemplate.delete(key);
    }

    public Map<String, Long> getCacheStatistics() {
        Map<String, Long> stats = new ConcurrentHashMap<>(cacheStats);
        
        stats.put("chatResponsesCacheSize", getCacheSize("chatResponses"));
        stats.put("embeddingsCacheSize", getCacheSize("embeddings"));
        stats.put("documentSegmentsCacheSize", getCacheSize("documentSegments"));
        
        return stats;
    }

    private void updateCacheStats(String cacheName) {
        cacheStats.merge(cacheName + "_hits", 1L, Long::sum);
    }

    private Long getCacheSize(String cacheName) {
        try {
            var keys = redisTemplate.keys(cacheName + "*");
            return keys != null ? (long) keys.size() : 0L;
        } catch (Exception e) {
            log.warn("Failed to get cache size for {}: {}", cacheName, e.getMessage());
            return 0L;
        }
    }
}