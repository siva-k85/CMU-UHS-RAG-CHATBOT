package edu.cmu.uhs.chatbot.model;

import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatMetric {
    private String id;
    private String sessionId;
    private String query;
    private String response;
    private LocalDateTime timestamp;
    private Long responseTimeMs;
    private Integer responseLength;
    private Integer queryLength;
    private List<String> categories;
    private Integer citationsCount;
    private Integer relevantDocsCount;
    private String llmProvider;
    private Boolean wasSuccessful;
    private String errorType;
    private Map<String, Object> metadata;
    
    // Calculated fields
    private Double sentimentScore;
    private String queryType; // question, command, statement
    private String topic; // insurance, appointments, hours, etc.
}