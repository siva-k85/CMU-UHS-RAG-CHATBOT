# CMU Health Services RAG Chatbot - Codex Setup Guide

## Exact Configuration for OpenAI Codex

Copy and paste these exact values into your Codex environment configuration:

### Environment Variables
```
SPRING_PROFILES_ACTIVE=dev
NODE_ENV=development
JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8080
GRADLE_USER_HOME=/root/.gradle
```

### Setup Script
```bash
# Configure Java to use Java 21 (available in Codex) instead of Java 17
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

# Create gradle wrapper if missing
if [ ! -f "./gradlew" ]; then
  gradle wrapper --gradle-version 8.5
fi

# Backend setup - configure Gradle to use Java 21
chmod +x ./gradlew
./gradlew clean build -x test -Dorg.gradle.java.home=$JAVA_HOME || echo "Build failed, will configure toolchain"

# If build fails due to Java version, update build.gradle to use Java 21
if [ $? -ne 0 ]; then
  # Update build.gradle to use Java 21 instead of 17
  sed -i 's/languageVersion = JavaLanguageVersion.of(17)/languageVersion = JavaLanguageVersion.of(21)/g' build.gradle
  # Try build again
  ./gradlew clean build -x test
fi

# Frontend setup
cd frontend
npm install
cd ..

# Python dependencies for scrapers
pip install beautifulsoup4==4.12.3 requests==2.31.0 lxml==5.1.0

# Create necessary directories
mkdir -p data/scraped_latest
mkdir -p frontend/public
mkdir -p build/libs

# Set executable permissions
chmod +x ./gradlew
chmod +x run-full-stack.sh || true
chmod +x deploy/gcp-deploy.sh || true
```

### Agent Internet Access Configuration
- **Status:** On
- **Domain Allowlist:** Common dependencies
- **Additional domains to add:**
  ```
  cmu.edu
  anthropic.com
  claude.ai
  ```
- **Allowed HTTP Methods:** GET, HEAD, OPTIONS

## AGENTS.md File Content

Create this file in your repository root:

```markdown
# CMU Health Services RAG Chatbot - Agent Guidelines

## Project Overview
Spring Boot + Next.js application providing an AI-powered chatbot for CMU Health Services using RAG with Anthropic's Claude API.

## Project Structure
- Root directory contains Gradle build files (build.gradle, gradlew)
- `src/` - Java Spring Boot backend source code
- `frontend/` - Next.js frontend application
- `scraper/` - Python web scraping tools
- `data/` - Knowledge base and scraped data
- `deploy/` - Deployment configurations

## Build Commands
- Backend: `./gradlew bootRun`
- Backend build: `./gradlew build`
- Backend test: `./gradlew test`
- Frontend dev: `cd frontend && npm run dev`
- Frontend build: `cd frontend && npm run build`
- Frontend lint: `cd frontend && npm run lint`
- Scraper: `cd scraper && python latest_health_scraper.py`

## Key Files
- Backend main: `src/main/java/edu/cmu/uhs/chatbot/RagChatbotApplication.java`
- Chat controller: `src/main/java/edu/cmu/uhs/chatbot/controller/ChatController.java`
- Anthropic service: `src/main/java/edu/cmu/uhs/chatbot/service/AnthropicService.java`
- Frontend main: `frontend/src/app/page.tsx`
- Analytics: `frontend/src/app/analytics/page.tsx`
- Health scraper: `scraper/latest_health_scraper.py`

## Testing Guidelines
- Always run `./gradlew test` before committing backend changes
- Run `cd frontend && npm run lint` before committing frontend changes
- Test the full stack with both backend and frontend running
- Verify CORS settings if experiencing cross-origin issues

## API Endpoints
- Chat: POST http://localhost:8080/api/v2/chat
- Metrics: GET http://localhost:8080/api/v1/metrics/dashboard
- Document upload: POST http://localhost:8080/api/v1/documents/upload
- Health check: GET http://localhost:8080/api/health

## Environment Requirements
- Java 17+ (project uses Java 17)
- Node.js 20+
- Python 3.8+
- Gradle 8.5+

## Common Issues
- If gradlew is missing, run: `gradle wrapper --gradle-version 8.5`
- CORS errors: Check WebConfig.java in backend
- Port conflicts: Backend uses 8080, Frontend uses 3000
- Anthropic API key: Must be set in environment variables

## PR Guidelines
- Title: `[backend|frontend|scraper] Brief description`
- Run all tests before submitting
- Update knowledge base if changing health information
- Maintain CMU branding (color: #C41E3A)
```

## Ready-to-Use Codex Prompts

### 1. Fix Java Version and Build Issues
```
Update the project to use Java 21 and fix build issues:
1. Edit build.gradle and change JavaLanguageVersion.of(17) to JavaLanguageVersion.of(21)
2. Run ./gradlew clean build -x test to verify the build works
3. If there are any Java compatibility issues, fix them
4. Ensure all Spring Boot dependencies are compatible with Java 21
5. Test that the application starts with ./gradlew bootRun
```

### 2. Implement Caching
```
Add Redis caching to improve chatbot performance:
1. Add Redis dependencies to build.gradle
2. Configure Redis connection in application.properties
3. Implement caching in ChatbotService for frequent queries
4. Add cache eviction strategy for updated content
5. Create cache statistics endpoint
6. Test with docker-compose Redis service
```

### 3. Enhance Security
```
Review and enhance security:
1. Audit AnthropicService.java for API key exposure
2. Check CORS configuration in backend
3. Add input validation for chat messages
4. Implement rate limiting using Spring annotations
5. Add request logging with sensitive data masking
6. Create security documentation
```

### 4. Add User Sessions
```
Implement user session management:
1. Add session tracking to ChatController
2. Store chat history per session in memory
3. Create session cleanup mechanism (30 min timeout)
4. Add session ID to frontend requests
5. Display session history in UI
6. Add session analytics to metrics
```

### 5. Improve RAG Pipeline
```
Enhance the RAG implementation:
1. Review VectorStoreService implementation
2. Add semantic search capabilities
3. Implement chunk overlap for better context
4. Add relevance scoring to responses
5. Create endpoint to test vector similarity
6. Document the RAG pipeline architecture
```

### 6. Frontend Performance
```
Optimize frontend performance:
1. Add React.memo to chat message components
2. Implement virtual scrolling for long chat histories
3. Add lazy loading for analytics charts
4. Optimize bundle size with dynamic imports
5. Add service worker for offline support
6. Measure and report Core Web Vitals
```

### 7. Scraper Enhancement
```
Improve the web scraper:
1. Review latest_health_scraper.py
2. Add retry logic for failed requests
3. Implement incremental updates (only new content)
4. Add content change detection
5. Create scraping schedule automation
6. Add scraping metrics and logging
```

### 8. Testing Suite
```
Create comprehensive test suite:
1. Add JUnit tests for all service classes
2. Create integration tests for REST endpoints
3. Add React Testing Library tests for frontend
4. Create E2E tests with Playwright
5. Add test coverage reporting
6. Set up GitHub Actions for CI/CD
```

### 9. Documentation
```
Create technical documentation:
1. Generate JavaDoc for all backend classes
2. Add JSDoc comments to TypeScript code
3. Create API documentation with Swagger
4. Document deployment process
5. Create architecture diagrams
6. Add troubleshooting guide
```

### 10. Monitoring Setup
```
Implement application monitoring:
1. Add Spring Boot Actuator endpoints
2. Configure health checks
3. Add custom metrics for chat usage
4. Implement structured logging
5. Create Grafana dashboard config
6. Add alerting rules
```

## Quick Debugging Commands

If Codex encounters issues, these commands help diagnose:

```bash
# Check Java version
java -version

# Check Gradle
./gradlew --version

# Check Node/npm
node --version && npm --version

# List project structure
find . -type f -name "*.java" | head -20
find frontend -type f -name "*.tsx" | head -20

# Check for build artifacts
ls -la build/libs/
ls -la frontend/.next/

# View application config
cat src/main/resources/application.properties
```

## Important: Java Version Issue

The project specifies Java 17 in build.gradle, but Codex comes with Java 21. The setup script above handles this automatically. If you still encounter Java version issues, use this **Alternative Simple Setup Script**:

### Alternative Simple Setup Script (Skip Backend Build)
```bash
# Skip backend build if Java version causes issues
echo "Skipping backend build due to Java version mismatch"

# Frontend setup
cd frontend
npm install
cd ..

# Python dependencies for scrapers
pip install beautifulsoup4==4.12.3 requests==2.31.0 lxml==5.1.0

# Create necessary directories
mkdir -p data/scraped_latest
mkdir -p frontend/public
mkdir -p src/main/resources
mkdir -p src/main/java/edu/cmu/uhs/chatbot

# Set executable permissions
chmod +x ./gradlew || true
chmod +x run-full-stack.sh || true
```

Then in your Codex prompt, ask it to:
1. First update build.gradle to use Java 21
2. Then build the backend

## Notes

- The project uses Gradle, not Maven
- Java 17 is specified in build.gradle but Codex has Java 21 (compatible with modification)
- Frontend uses Next.js with Turbopack for faster development
- The backend is a standard Spring Boot application
- Python scrapers use BeautifulSoup4 for web scraping