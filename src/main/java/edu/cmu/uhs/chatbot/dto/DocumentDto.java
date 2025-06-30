package edu.cmu.uhs.chatbot.dto;

import lombok.Data;
import java.util.Map;

@Data
public class DocumentDto {
    private String content;
    private Map<String, Object> metadata;
}