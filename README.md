# CMU UHS RAG Chatbot

A comprehensive Retrieval-Augmented Generation (RAG) chatbot system designed for Carnegie Mellon University Health Services. This application provides intelligent, context-aware responses to health-related queries by leveraging CMU UHS documentation and resources.

## 🌟 Features

### Core Functionality
- **RAG-powered Chat Interface**: Intelligent responses using retrieval-augmented generation
- **Multi-Model Support**: Integration with OpenAI GPT and Anthropic Claude models
- **Document Management**: Upload and process various document formats (PDF, TXT, MD)
- **Web Scraping**: Automated ingestion of CMU health services web content
- **Vector Search**: Semantic search using pgvector for accurate information retrieval
- **Caching Layer**: Redis-based caching for improved performance
- **Analytics Dashboard**: Real-time metrics and usage analytics

### Technical Features
- **Microservices Architecture**: Separated frontend and backend services
- **Containerization**: Full Docker support with docker-compose
- **Database Persistence**: PostgreSQL with pgvector extension
- **Modern UI**: Next.js frontend with Tailwind CSS
- **RESTful API**: Well-documented API endpoints
- **Health Monitoring**: Built-in health checks and metrics

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Next.js UI    │────▶│  Spring Boot    │────▶│  PostgreSQL     │
│   (Frontend)    │     │    Backend      │     │   + pgvector    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────┐          ┌─────────────┐
                        │    Redis    │          │   Vector    │
                        │    Cache    │          │    Store    │
                        └─────────────┘          └─────────────┘
                               │
                               ▼
                        ┌─────────────────────────────┐
                        │   LLM APIs                  │
                        │  - OpenAI GPT               │
                        │  - Anthropic Claude         │
                        └─────────────────────────────┘
```

## 📋 Prerequisites

- **Java 17+** (for backend)
- **Node.js 18+** (for frontend)
- **Docker & Docker Compose** (for containerized deployment)
- **Maven 3.6+** (for building backend)
- **API Keys**:
  - OpenAI API key (required)
  - Anthropic API key (optional, for Claude support)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/CMU-UHS-RAG-CHATBOT.git
   cd CMU-UHS-RAG-CHATBOT
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and configurations
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - API Documentation: http://localhost:8080/swagger-ui.html

### Manual Setup

#### Backend Setup

1. **Configure environment variables**
   ```bash
   export OPENAI_API_KEY=your-openai-api-key
   export ANTHROPIC_API_KEY=your-anthropic-api-key  # Optional
   ```

2. **Install PostgreSQL with pgvector**
   ```bash
   # Install PostgreSQL and pgvector extension
   # Run init-db.sql to set up the database schema
   ```

3. **Build and run the backend**
   ```bash
   cd backend
   mvn clean install
   mvn spring-boot:run
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API endpoint**
   ```bash
   # Create .env.local file
   echo "NEXT_PUBLIC_API_URL=http://localhost:8080" > .env.local
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

## 📝 Usage Guide

### Chat Interface

1. Navigate to http://localhost:3000
2. Type your health-related question in the chat input
3. The system will search relevant CMU UHS documents and provide an informed response
4. Responses include source citations for transparency

### Document Management

#### Upload Documents
```bash
# Via API
curl -X POST http://localhost:8080/api/v1/documents/upload \
  -F "file=@your-document.pdf" \
  -F "metadata={\"source\":\"manual_upload\"}"
```

#### Ingest Directory
```bash
# Process all documents in a directory
curl -X POST http://localhost:8080/api/v1/documents/ingest-directory \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/documents"}'
```

### Web Scraping

The scraper automatically processes CMU health services websites:

```bash
cd scraper
python run_scraper_and_ingest.py
```

## 🔌 API Endpoints

### Chat Endpoints
- `POST /api/v1/chat` - Send a chat message
- `POST /api/v1/chat/enhanced` - Chat with enhanced features
- `GET /api/v1/chat/history` - Get chat history

### Document Endpoints
- `POST /api/v1/documents/upload` - Upload a single document
- `POST /api/v1/documents/batch` - Upload multiple documents
- `POST /api/v1/documents/ingest-directory` - Ingest documents from directory
- `GET /api/v1/documents` - List all documents
- `DELETE /api/v1/documents/{id}` - Delete a document

### Analytics Endpoints
- `GET /api/v1/metrics` - Get usage metrics
- `GET /api/v1/metrics/analytics` - Get detailed analytics

### System Endpoints
- `GET /api/v1/health` - Health check
- `GET /api/v1/info` - System information

## 🔧 Configuration

### Application Properties

Key configuration options in `application.properties`:

```properties
# Vector Store Configuration
vector.store.dimension=384
vector.store.similarity.threshold=0.7

# LLM Configuration
llm.model.name=gpt-4
llm.temperature=0.7
llm.max.tokens=1000

# Cache Configuration
cache.ttl.minutes=60
cache.max.size=1000
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | No | - |
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes | changeme |
| `REDIS_PASSWORD` | Redis password | Yes | changeme |
| `SPRING_PROFILES_ACTIVE` | Active Spring profile | No | default |

## 📊 Analytics & Monitoring

The system includes comprehensive analytics:

- **Usage Metrics**: Track queries, response times, and user engagement
- **Performance Monitoring**: Monitor vector search performance and LLM latency
- **Error Tracking**: Log and analyze system errors
- **Health Checks**: Automated health monitoring for all services

Access the analytics dashboard at: http://localhost:3000/analytics

## 🧪 Testing

### Run Unit Tests
```bash
# Backend tests
cd backend
mvn test

# Frontend tests
cd frontend
npm test
```

### Run Integration Tests
```bash
mvn verify -Pintegration-tests
```

## 🚢 Deployment

### Docker Deployment

1. **Build images**
   ```bash
   docker-compose build
   ```

2. **Deploy with production config**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Kubernetes Deployment

Deploy to Kubernetes cluster:

```bash
cd deploy/k8s
kubectl apply -f .
```

### Google Cloud Platform

Deploy to GCP:

```bash
cd deploy
./gcp-deploy.sh
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Carnegie Mellon University Health Services for providing the domain expertise
- The open-source community for the amazing tools and libraries used in this project
- Contributors and testers who helped improve the system

## 📞 Support

For support, please:
- Check the [documentation](./docs)
- Open an issue on GitHub
- Contact the development team at [email]

---

Built with ❤️ for the CMU community