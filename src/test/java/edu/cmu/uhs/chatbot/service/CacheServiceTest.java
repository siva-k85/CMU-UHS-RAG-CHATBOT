package edu.cmu.uhs.chatbot.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CacheServiceTest {

    @Mock
    private RedisTemplate<String, Object> redisTemplate;

    @Mock
    private ValueOperations<String, Object> valueOperations;

    @InjectMocks
    private CacheService cacheService;

    @BeforeEach
    void setUp() {
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
    }

    @Test
    void testCacheResponse() {
        String query = "test query";
        String response = "test response";

        String cachedResponse = cacheService.cacheResponse(query, response);

        assertEquals(response, cachedResponse);
    }

    @Test
    void testGetCachedResponse() {
        String query = "test query";

        String result = cacheService.getCachedResponse(query);

        assertNull(result);
    }

    @Test
    void testCacheEmbedding() {
        String text = "test text";
        List<Float> embedding = List.of(0.1f, 0.2f, 0.3f);

        List<Float> result = cacheService.cacheEmbedding(text, embedding);

        assertEquals(embedding, result);
    }

    @Test
    void testGetCachedEmbedding() {
        String text = "test text";

        List<Float> result = cacheService.getCachedEmbedding(text);

        assertNull(result);
    }

    @Test
    void testCacheDocumentSegments() {
        String documentId = "doc123";
        List<String> segments = List.of("segment1", "segment2", "segment3");

        List<String> result = cacheService.cacheDocumentSegments(documentId, segments);

        assertEquals(segments, result);
    }

    @Test
    void testSetCacheWithTTL() {
        String key = "test-key";
        String value = "test-value";
        Duration ttl = Duration.ofMinutes(30);

        cacheService.setCacheWithTTL(key, value, ttl);

        verify(valueOperations).set(key, value, ttl);
    }

    @Test
    void testGetFromCache() {
        String key = "test-key";
        String expectedValue = "test-value";
        when(valueOperations.get(key)).thenReturn(expectedValue);

        Object result = cacheService.getFromCache(key);

        assertEquals(expectedValue, result);
        verify(valueOperations).get(key);
    }

    @Test
    void testRemoveFromCache() {
        String key = "test-key";
        when(redisTemplate.delete(key)).thenReturn(true);

        cacheService.removeFromCache(key);

        verify(redisTemplate).delete(key);
    }

    @Test
    void testGetCacheStatistics() {
        when(redisTemplate.keys(anyString())).thenReturn(Set.of("key1", "key2"));

        Map<String, Long> stats = cacheService.getCacheStatistics();

        assertNotNull(stats);
        assertTrue(stats.containsKey("chatResponsesCacheSize"));
        assertTrue(stats.containsKey("embeddingsCacheSize"));
        assertTrue(stats.containsKey("documentSegmentsCacheSize"));
    }

    @Test
    void testClearAllCaches() {
        cacheService.clearAllCaches();

        Map<String, Long> stats = cacheService.getCacheStatistics();
        assertNotNull(stats);
    }

    @Test
    void testGetCacheStatisticsWithException() {
        when(redisTemplate.keys(anyString())).thenThrow(new RuntimeException("Redis error"));

        Map<String, Long> stats = cacheService.getCacheStatistics();

        assertNotNull(stats);
        assertEquals(0L, stats.get("chatResponsesCacheSize"));
    }

    @Test
    void testCacheResponseUpdatesStats() {
        String query = "test query";
        String response = "test response";

        cacheService.cacheResponse(query, response);

        Map<String, Long> stats = cacheService.getCacheStatistics();
        assertNotNull(stats);
    }

    @Test
    void testClearChatCache() {
        cacheService.clearChatCache();

        Map<String, Long> stats = cacheService.getCacheStatistics();
        assertNotNull(stats);
    }

    @Test
    void testClearEmbeddingCache() {
        cacheService.clearEmbeddingCache();

        Map<String, Long> stats = cacheService.getCacheStatistics();
        assertNotNull(stats);
    }
}