package edu.cmu.uhs.chatbot.model;

import lombok.Data;

@Data
public class ChatRequest {
    private String message;

    // Transcript text if voice input was provided
    private String voiceTranscript;

    // Descriptions of any images included with the query
    private java.util.List<String> imageDescriptions;

    // Descriptions of medical scans or documents
    private java.util.List<String> medicalScanDescriptions;
}