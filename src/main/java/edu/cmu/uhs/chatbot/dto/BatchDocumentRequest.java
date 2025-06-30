package edu.cmu.uhs.chatbot.dto;

import lombok.Data;
import java.util.List;

@Data
public class BatchDocumentRequest {
    private List<DocumentDto> documents;
}