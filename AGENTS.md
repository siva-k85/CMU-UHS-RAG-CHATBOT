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