package edu.cmu.uhs.chatbot.controller;

import edu.cmu.uhs.chatbot.service.MetricsService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/metrics")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class MetricsController {
    
    private final MetricsService metricsService;
    
    @GetMapping("/overview")
    public ResponseEntity<Map<String, Object>> getOverview() {
        Map<String, Object> overview = new HashMap<>();
        overview.put("stats", metricsService.getOverallStats());
        overview.put("topicDistribution", metricsService.getTopicDistribution());
        overview.put("responseTimeStats", metricsService.getResponseTimeStats());
        overview.put("queryTypes", metricsService.getQueryTypeDistribution());
        return ResponseEntity.ok(overview);
    }
    
    @GetMapping("/activity/hourly")
    public ResponseEntity<Map<String, Object>> getHourlyActivity() {
        Map<String, Object> data = new HashMap<>();
        data.put("hourly", metricsService.getHourlyActivity());
        data.put("timeSeries", metricsService.getTimeSeriesData(24));
        return ResponseEntity.ok(data);
    }
    
    @GetMapping("/queries/recent")
    public ResponseEntity<Map<String, Object>> getRecentQueries(
            @RequestParam(defaultValue = "10") int limit) {
        Map<String, Object> data = new HashMap<>();
        data.put("queries", metricsService.getRecentQueries(limit));
        return ResponseEntity.ok(data);
    }
    
    @GetMapping("/queries/popular")
    public ResponseEntity<Map<String, Object>> getPopularQueries(
            @RequestParam(defaultValue = "10") int limit) {
        Map<String, Object> data = new HashMap<>();
        data.put("popular", metricsService.getPopularQueries(limit));
        return ResponseEntity.ok(data);
    }
    
    @GetMapping("/sessions")
    public ResponseEntity<Map<String, Object>> getSessionStats() {
        return ResponseEntity.ok(metricsService.getSessionStats());
    }
    
    @GetMapping("/dashboard")
    public ResponseEntity<Map<String, Object>> getDashboardData() {
        Map<String, Object> dashboard = new HashMap<>();
        dashboard.put("overview", metricsService.getOverallStats());
        dashboard.put("topics", metricsService.getTopicDistribution());
        dashboard.put("hourlyActivity", metricsService.getHourlyActivity());
        dashboard.put("recentQueries", metricsService.getRecentQueries(5));
        dashboard.put("popularQueries", metricsService.getPopularQueries(5));
        dashboard.put("responseTime", metricsService.getResponseTimeStats());
        dashboard.put("queryTypes", metricsService.getQueryTypeDistribution());
        dashboard.put("sessions", metricsService.getSessionStats());
        dashboard.put("timeSeries", metricsService.getTimeSeriesData(24));
        return ResponseEntity.ok(dashboard);
    }
}