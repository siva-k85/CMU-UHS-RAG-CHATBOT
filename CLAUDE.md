# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Build and Run
```bash
# Using Maven
mvn clean install                  # Build the project
mvn spring-boot:run               # Run the application
mvn test                          # Run tests

# Using Gradle (alternative)
./gradlew clean build             # Build the project
./gradlew bootRun                 # Run the application
./gradlew test                    # Run tests

# Environment setup (required)
export OPENAI_API_KEY=your-api-key-here    # Must be set before running
```

### Java Version Requirements
- **Required**: Java 17 or 21 (Spring Boot 3.2.5 compatibility)
- **Not compatible**: Java 24+
- Check version: `java -version`
- Switch Java version on macOS: `export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home`

## Architecture Overview

### RAG Implementation Stack
The application implements a Retrieval-Augmented Generation system using:

1. **Document Ingestion Pipeline**
   - `DocumentIngestionService` processes PDF, TXT, and MD files
   - Uses Apache PDFBox for PDF parsing via LangChain4j
   - Documents are chunked and converted to embeddings using all-MiniLM-L6-v2
   - Auto-ingests from `/data` directory on startup via `DataInitializer`

2. **Vector Storage and Retrieval**
   - `VectorStoreService` manages in-memory vector storage
   - Semantic search finds top-k relevant document segments
   - No persistence - vectors are rebuilt on each restart
   - Uses cosine similarity for relevance scoring

3. **LLM Integration**
   - `ChatbotService` orchestrates RAG flow: query → retrieve context → augment prompt → generate
   - OpenAI GPT-3.5-turbo for response generation
   - Fallback responses when API key is missing or invalid
   - Context window management with MAX_RELEVANT_DOCUMENTS=5

4. **API Layer**
   - `ChatController` exposes REST endpoints
   - CORS enabled for all origins
   - File upload limit: 10MB
   - Endpoints: `/api/v1/chat`, `/api/v1/documents/upload`, `/api/v1/health`

### Key Design Decisions
- **In-memory storage**: Simplicity over persistence (consider Pinecone/Chroma for production)
- **Synchronous processing**: Document upload blocks until embedding complete
- **Single embedding model**: all-MiniLM-L6-v2 balances quality and performance
- **Context injection**: Retrieved documents are injected into system prompt, not user message

## CMU Health Services Context
The system is pre-loaded with CMU UHS information from `/data/cmu-uhs-info.md` including:
- Service locations and hours
- Available health services (primary care, mental health, etc.)
- Insurance and billing information
- Appointment scheduling procedures

When extending the knowledge base, maintain similar structure and include metadata like service hours, contact info, and procedural details that students commonly ask about.

## Common Development Tasks

### Adding New Document Types
1. Extend `DocumentIngestionService.processFile()` to handle new MIME types
2. Add corresponding parser dependency in `pom.xml`
3. Update `isSupportedFileType()` validation

### Switching Vector Databases
Current implementation uses in-memory storage. To add persistence:
1. Replace `VectorStoreService` implementation
2. Add vector DB client dependency (e.g., `langchain4j-pinecone`)
3. Update application.properties with connection details
4. Implement data migration strategy for existing embeddings

### Customizing the Chatbot Persona
Edit the system prompt in `ChatbotService.buildPrompt()` to adjust:
- Response tone and formality
- Scope of answers (CMU-specific vs general health)
- Handling of out-of-scope questions

### Performance Optimization
- Adjust `MAX_RELEVANT_DOCUMENTS` for accuracy vs token usage trade-off
- Consider caching frequent queries in `ChatbotService`
- Implement async document processing for large uploads
- Add connection pooling for vector store operations