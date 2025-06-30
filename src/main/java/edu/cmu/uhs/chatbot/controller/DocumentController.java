package edu.cmu.uhs.chatbot.controller;

import edu.cmu.uhs.chatbot.dto.BatchDocumentRequest;
import edu.cmu.uhs.chatbot.dto.DocumentDto;
import edu.cmu.uhs.chatbot.service.VectorStoreService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/documents")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class DocumentController {

    private final VectorStoreService vectorStoreService;

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadDocument(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "source", defaultValue = "upload") String source) {
        
        log.info("Received file upload: {} from source: {}", file.getOriginalFilename(), source);
        
        try {
            vectorStoreService.addDocument(file, source);
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Document uploaded successfully");
            response.put("filename", file.getOriginalFilename());
            response.put("size", file.getSize());
            response.put("source", source);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("Error uploading document", e);
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to upload document: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @PostMapping("/batch")
    public ResponseEntity<Map<String, Object>> uploadBatchDocuments(
            @RequestBody BatchDocumentRequest request) {
        
        log.info("Received batch upload with {} documents", request.getDocuments().size());
        
        try {
            int successCount = 0;
            int failCount = 0;
            
            for (DocumentDto doc : request.getDocuments()) {
                try {
                    vectorStoreService.addDocumentFromText(
                        doc.getContent(),
                        doc.getMetadata()
                    );
                    successCount++;
                } catch (Exception e) {
                    log.error("Failed to process document: {}", e.getMessage());
                    failCount++;
                }
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Batch upload completed");
            response.put("total", request.getDocuments().size());
            response.put("success", successCount);
            response.put("failed", failCount);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("Error in batch upload", e);
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to process batch: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/count")
    public ResponseEntity<Map<String, Object>> getDocumentCount() {
        try {
            int count = vectorStoreService.getDocumentCount();
            
            Map<String, Object> response = new HashMap<>();
            response.put("count", count);
            response.put("status", "active");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("Error getting document count", e);
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to get count: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @DeleteMapping("/clear")
    public ResponseEntity<Map<String, Object>> clearDocuments() {
        try {
            vectorStoreService.clearDocuments();
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "All documents cleared successfully");
            response.put("status", "cleared");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("Error clearing documents", e);
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to clear documents: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }
}