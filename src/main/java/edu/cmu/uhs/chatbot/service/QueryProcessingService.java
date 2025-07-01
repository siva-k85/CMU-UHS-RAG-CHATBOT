package edu.cmu.uhs.chatbot.service;

import edu.cmu.uhs.chatbot.model.ChatRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

@Service
@Slf4j
public class QueryProcessingService {

    private static final Map<String, String[]> MEDICAL_SYNONYMS = new HashMap<>();

    static {
        MEDICAL_SYNONYMS.put("flu", new String[]{"influenza"});
        MEDICAL_SYNONYMS.put("bp", new String[]{"blood pressure"});
        MEDICAL_SYNONYMS.put("uti", new String[]{"urinary tract infection"});
    }

    /**
     * Combine multi-modal inputs and expand medical abbreviations.
     * @param request chat request
     * @return expanded query string
     */
    public String processQuery(ChatRequest request) {
        StringBuilder combined = new StringBuilder();
        if (request.getMessage() != null) {
            combined.append(request.getMessage()).append(" ");
        }
        if (request.getVoiceTranscript() != null) {
            combined.append(request.getVoiceTranscript()).append(" ");
        }
        if (request.getImageDescriptions() != null) {
            request.getImageDescriptions().forEach(d -> combined.append(d).append(" "));
        }
        if (request.getMedicalScanDescriptions() != null) {
            request.getMedicalScanDescriptions().forEach(d -> combined.append(d).append(" "));
        }

        String expanded = expandSynonyms(combined.toString().trim());
        return reformulateQuery(expanded);
    }

    /**
     * Simple keyword-based intent classification for healthcare queries.
     */
    public String classifyIntent(String query) {
        String lower = query.toLowerCase(Locale.ROOT);
        if (lower.contains("appointment")) return "appointment";
        if (lower.contains("hours") || lower.contains("open")) return "hours";
        if (lower.contains("location") || lower.contains("where")) return "location";
        if (lower.contains("service")) return "service";
        return "general";
    }

    private String expandSynonyms(String query) {
        String lower = query.toLowerCase(Locale.ROOT);
        StringBuilder expanded = new StringBuilder(query);
        for (Map.Entry<String, String[]> entry : MEDICAL_SYNONYMS.entrySet()) {
            if (lower.contains(entry.getKey())) {
                for (String syn : entry.getValue()) {
                    expanded.append(' ').append(syn);
                }
            }
        }
        return expanded.toString();
    }

    /**
     * Placeholder for context-aware query reformulation.
     * Currently trims and normalizes whitespace.
     */
    private String reformulateQuery(String query) {
        return query.replaceAll("\\s+", " ").trim();
    }
}
