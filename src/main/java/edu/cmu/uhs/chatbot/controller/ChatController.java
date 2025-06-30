package edu.cmu.uhs.chatbot.controller;

import edu.cmu.uhs.chatbot.model.ChatRequest;
import edu.cmu.uhs.chatbot.model.ChatResponse;
import edu.cmu.uhs.chatbot.service.ChatbotService;
import edu.cmu.uhs.chatbot.service.DocumentIngestionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class ChatController {
    
    private final ChatbotService chatbotService;
    private final DocumentIngestionService documentIngestionService;
    
    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest request) {
        log.info("Received chat request: {}", request.getMessage());
        
        try {
            String response = chatbotService.chat(request.getMessage());
            return ResponseEntity.ok(new ChatResponse(response));
        } catch (Exception e) {
            log.error("Error processing chat request", e);
            return ResponseEntity.internalServerError()
                    .body(new ChatResponse("I'm sorry, I encountered an error processing your request."));
        }
    }
    
    
    @PostMapping("/documents/ingest-directory")
    public ResponseEntity<String> ingestDirectory(@RequestParam String path) {
        log.info("Received directory ingestion request: {}", path);
        
        try {
            documentIngestionService.ingestDirectory(path);
            return ResponseEntity.ok("Directory ingested successfully");
        } catch (IOException e) {
            log.error("Error ingesting directory", e);
            return ResponseEntity.internalServerError()
                    .body("Error ingesting directory: " + e.getMessage());
        }
    }
    
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("CMU UHS RAG Chatbot is running");
    }
}