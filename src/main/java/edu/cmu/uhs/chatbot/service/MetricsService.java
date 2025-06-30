package edu.cmu.uhs.chatbot.service;

import edu.cmu.uhs.chatbot.model.ChatMetric;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Service
@Slf4j
public class MetricsService {
    
    // In-memory storage for metrics (in production, use a database)
    private final List<ChatMetric> metrics = Collections.synchronizedList(new ArrayList<>());
    private final Map<String, Integer> topicCounts = new ConcurrentHashMap<>();
    private final Map<String, Integer> hourlyActivity = new ConcurrentHashMap<>();
    private final Map<String, List<Long>> sessionResponseTimes = new ConcurrentHashMap<>();
    
    public void recordMetric(ChatMetric metric) {
        // Add unique ID
        metric.setId(UUID.randomUUID().toString());
        
        // Analyze and categorize the query
        analyzeQuery(metric);
        
        // Store metric
        metrics.add(metric);
        
        // Update aggregated data
        updateAggregates(metric);
        
        log.info("Recorded metric for query: {} ({}ms)", 
            metric.getQuery().substring(0, Math.min(50, metric.getQuery().length())), 
            metric.getResponseTimeMs());
    }
    
    private void analyzeQuery(ChatMetric metric) {
        String query = metric.getQuery().toLowerCase();
        
        // Determine query type
        if (query.contains("?") || query.startsWith("what") || query.startsWith("how") || 
            query.startsWith("when") || query.startsWith("where") || query.startsWith("why")) {
            metric.setQueryType("question");
        } else if (query.contains("tell me") || query.contains("show me") || query.contains("find")) {
            metric.setQueryType("command");
        } else {
            metric.setQueryType("statement");
        }
        
        // Determine topic
        String topic = "general";
        if (query.contains("insurance") || query.contains("ship") || query.contains("coverage")) {
            topic = "insurance";
        } else if (query.contains("appointment") || query.contains("schedule")) {
            topic = "appointments";
        } else if (query.contains("hour") || query.contains("open") || query.contains("close")) {
            topic = "hours";
        } else if (query.contains("mental") || query.contains("counseling") || query.contains("therapy")) {
            topic = "mental_health";
        } else if (query.contains("pharmacy") || query.contains("prescription") || query.contains("medication")) {
            topic = "pharmacy";
        } else if (query.contains("emergency") || query.contains("urgent")) {
            topic = "emergency";
        } else if (query.contains("location") || query.contains("where") || query.contains("address")) {
            topic = "location";
        } else if (query.contains("contact") || query.contains("phone") || query.contains("email")) {
            topic = "contact";
        }
        metric.setTopic(topic);
        
        // Simple sentiment analysis (in production, use NLP library)
        double sentiment = 0.5; // neutral
        if (query.contains("thank") || query.contains("great") || query.contains("good")) {
            sentiment = 0.8;
        } else if (query.contains("problem") || query.contains("issue") || query.contains("wrong")) {
            sentiment = 0.2;
        }
        metric.setSentimentScore(sentiment);
    }
    
    private void updateAggregates(ChatMetric metric) {
        // Update topic counts
        topicCounts.merge(metric.getTopic(), 1, Integer::sum);
        
        // Update hourly activity
        String hour = String.valueOf(metric.getTimestamp().getHour());
        hourlyActivity.merge(hour, 1, Integer::sum);
        
        // Update session response times
        sessionResponseTimes.computeIfAbsent(metric.getSessionId(), k -> new ArrayList<>())
            .add(metric.getResponseTimeMs());
    }
    
    // Analytics methods
    
    public Map<String, Object> getOverallStats() {
        Map<String, Object> stats = new HashMap<>();
        
        if (metrics.isEmpty()) {
            stats.put("totalQueries", 0);
            stats.put("avgResponseTime", 0);
            stats.put("successRate", 100);
            stats.put("totalSessions", 0);
            return stats;
        }
        
        stats.put("totalQueries", metrics.size());
        stats.put("avgResponseTime", metrics.stream()
            .mapToLong(ChatMetric::getResponseTimeMs)
            .average()
            .orElse(0));
        stats.put("successRate", metrics.stream()
            .filter(ChatMetric::getWasSuccessful)
            .count() * 100.0 / metrics.size());
        stats.put("totalSessions", metrics.stream()
            .map(ChatMetric::getSessionId)
            .distinct()
            .count());
        stats.put("avgQueriesPerSession", (double) metrics.size() / 
            metrics.stream().map(ChatMetric::getSessionId).distinct().count());
        
        return stats;
    }
    
    public Map<String, Integer> getTopicDistribution() {
        return new HashMap<>(topicCounts);
    }
    
    public Map<String, Integer> getHourlyActivity() {
        return new HashMap<>(hourlyActivity);
    }
    
    public List<Map<String, Object>> getRecentQueries(int limit) {
        return metrics.stream()
            .sorted((a, b) -> b.getTimestamp().compareTo(a.getTimestamp()))
            .limit(limit)
            .map(m -> {
                Map<String, Object> query = new HashMap<>();
                query.put("query", m.getQuery());
                query.put("timestamp", m.getTimestamp().toString());
                query.put("responseTime", m.getResponseTimeMs());
                query.put("topic", m.getTopic());
                query.put("success", m.getWasSuccessful());
                return query;
            })
            .collect(Collectors.toList());
    }
    
    public Map<String, Object> getResponseTimeStats() {
        Map<String, Object> stats = new HashMap<>();
        
        List<Long> times = metrics.stream()
            .map(ChatMetric::getResponseTimeMs)
            .sorted()
            .collect(Collectors.toList());
        
        if (times.isEmpty()) {
            stats.put("min", 0);
            stats.put("max", 0);
            stats.put("median", 0);
            stats.put("p95", 0);
            return stats;
        }
        
        stats.put("min", times.get(0));
        stats.put("max", times.get(times.size() - 1));
        stats.put("median", times.get(times.size() / 2));
        stats.put("p95", times.get((int) (times.size() * 0.95)));
        
        return stats;
    }
    
    public List<Map<String, Object>> getQueryTypeDistribution() {
        Map<String, Long> typeCounts = metrics.stream()
            .collect(Collectors.groupingBy(
                ChatMetric::getQueryType,
                Collectors.counting()
            ));
        
        return typeCounts.entrySet().stream()
            .map(e -> {
                Map<String, Object> item = new HashMap<>();
                item.put("type", e.getKey());
                item.put("count", e.getValue());
                return item;
            })
            .collect(Collectors.toList());
    }
    
    public List<Map<String, Object>> getTimeSeriesData(int hours) {
        LocalDateTime cutoff = LocalDateTime.now().minusHours(hours);
        
        Map<String, Long> hourlyCounts = metrics.stream()
            .filter(m -> m.getTimestamp().isAfter(cutoff))
            .collect(Collectors.groupingBy(
                m -> m.getTimestamp().truncatedTo(ChronoUnit.HOURS).toString(),
                Collectors.counting()
            ));
        
        return hourlyCounts.entrySet().stream()
            .sorted(Map.Entry.comparingByKey())
            .map(e -> {
                Map<String, Object> item = new HashMap<>();
                item.put("time", e.getKey());
                item.put("count", e.getValue());
                return item;
            })
            .collect(Collectors.toList());
    }
    
    public Map<String, Object> getSessionStats() {
        Map<String, Object> stats = new HashMap<>();
        
        Map<String, List<ChatMetric>> sessionMetrics = metrics.stream()
            .collect(Collectors.groupingBy(ChatMetric::getSessionId));
        
        stats.put("totalSessions", sessionMetrics.size());
        stats.put("avgQueriesPerSession", 
            sessionMetrics.values().stream()
                .mapToInt(List::size)
                .average()
                .orElse(0));
        
        // Session duration stats
        List<Long> durations = sessionMetrics.values().stream()
            .map(sessions -> {
                if (sessions.size() < 2) return 0L;
                LocalDateTime start = sessions.stream()
                    .map(ChatMetric::getTimestamp)
                    .min(LocalDateTime::compareTo)
                    .orElse(LocalDateTime.now());
                LocalDateTime end = sessions.stream()
                    .map(ChatMetric::getTimestamp)
                    .max(LocalDateTime::compareTo)
                    .orElse(LocalDateTime.now());
                return ChronoUnit.MINUTES.between(start, end);
            })
            .filter(d -> d > 0)
            .collect(Collectors.toList());
        
        stats.put("avgSessionDurationMinutes", 
            durations.stream().mapToLong(Long::longValue).average().orElse(0));
        
        return stats;
    }
    
    public List<Map<String, Object>> getPopularQueries(int limit) {
        Map<String, Long> queryCounts = metrics.stream()
            .collect(Collectors.groupingBy(
                m -> m.getQuery().toLowerCase().trim(),
                Collectors.counting()
            ));
        
        return queryCounts.entrySet().stream()
            .sorted((a, b) -> b.getValue().compareTo(a.getValue()))
            .limit(limit)
            .map(e -> {
                Map<String, Object> item = new HashMap<>();
                item.put("query", e.getKey());
                item.put("count", e.getValue());
                return item;
            })
            .collect(Collectors.toList());
    }
}