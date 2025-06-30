package edu.cmu.uhs.chatbot.config;

import edu.cmu.uhs.chatbot.service.DocumentIngestionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Configuration
@RequiredArgsConstructor
@Slf4j
public class DataInitializer {
    
    private final DocumentIngestionService documentIngestionService;
    
    @Bean
    CommandLineRunner initData() {
        return args -> {
            String dataPath = "data";
            Path dataDir = Paths.get(dataPath);
            
            if (Files.exists(dataDir) && Files.isDirectory(dataDir)) {
                log.info("Initializing knowledge base from directory: {}", dataPath);
                try {
                    documentIngestionService.ingestDirectory(dataPath);
                    log.info("Knowledge base initialized successfully");
                } catch (Exception e) {
                    log.error("Error initializing knowledge base", e);
                }
            } else {
                log.warn("Data directory not found: {}. Please create it and add CMU UHS documents.", dataPath);
            }
        };
    }
}