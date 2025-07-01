# CMU UHS RAG Chatbot - Production Ready

This repository contains a production-ready Retrieval-Augmented Generation (RAG) chatbot for Carnegie Mellon University Health Services.

## ✅ Clean Repository Structure

### Core Application
- **Spring Boot 3.2.5** backend with modular service architecture
- **Next.js** frontend with modern React components
- **LangChain4j** for RAG implementation
- **Production-ready** security, caching, and monitoring

### Key Features
1. **Vector Storage**
   - Primary: ChromaDB for persistent storage
   - Fallback: In-memory storage
   - Automatic failover

2. **Caching Layer**
   - Redis integration for performance
   - Configurable TTL
   - Response and embedding caching

3. **Security**
   - JWT authentication ready
   - CORS configuration
   - Dev/Prod profile separation

4. **Monitoring**
   - Health check endpoints
   - Actuator integration
   - Prometheus metrics

5. **Testing**
   - Comprehensive unit tests
   - Service layer coverage
   - Mock implementations

## 🚀 Quick Start

```bash
# Set environment variables
export OPENAI_API_KEY=your-key  # Or use ANTHROPIC_API_KEY

# Run locally
./run-local.sh

# Or use Docker
docker-compose up
```

## 📁 Repository Structure

```
├── src/main/java/edu/cmu/uhs/chatbot/
│   ├── config/         # Spring configurations
│   ├── controller/     # REST endpoints
│   ├── service/        # Business logic
│   ├── model/          # Data models
│   └── dto/            # Data transfer objects
├── src/test/           # Unit tests
├── frontend/           # Next.js application
├── scraper/            # Data collection scripts
├── data/               # Knowledge base documents
├── deploy/             # Deployment configurations
└── docs/               # Documentation
```

## 🔧 Configuration

### Development Mode
- Security disabled
- CORS open
- In-memory defaults

### Production Mode
- JWT security enabled
- Configured CORS
- External services required

## 📊 Available Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/chat` - Chat interface
- `GET /actuator/health` - Detailed health
- `GET /actuator/metrics` - Application metrics
- `GET /actuator/prometheus` - Prometheus metrics

## 🛠 Technology Stack

- **Backend**: Spring Boot, Java 17
- **Frontend**: Next.js, React, TypeScript
- **Vector DB**: ChromaDB / In-memory
- **Cache**: Redis
- **LLM**: OpenAI GPT / Anthropic Claude
- **Build**: Gradle / Maven
- **Deploy**: Docker, Kubernetes ready

## 📝 Notes

- All test files, backups, and temporary code have been removed
- Production configurations are environment-variable driven
- Comprehensive .gitignore prevents accidental commits
- Clean separation between dev and prod profiles

This is a clean, production-ready codebase suitable for deployment.