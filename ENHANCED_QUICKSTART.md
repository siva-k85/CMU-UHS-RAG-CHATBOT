# 🚀 Enhanced CMU Health Services Chatbot - Quick Start Guide

## Overview
This production-ready RAG chatbot provides CMU students with instant access to health services information through a modern, accessible interface with AI-powered responses.

## ✨ Key Enhancements
- 🎤 **Voice Input**: Speak your questions naturally
- 📊 **Real-time Analytics**: Track usage and performance metrics
- 📚 **Smart Citations**: Verify information sources instantly
- 📱 **Mobile-First Design**: Works perfectly on all devices
- ⚡ **Lightning Fast**: Cached responses for common queries
- 🎨 **Modern Healthcare UI**: Calming colors and smooth animations

## 🛠️ Prerequisites
- Java 17 or 21
- Node.js 18+
- Maven or Gradle
- (Optional) Docker for Chroma/Redis

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd uhs-chatbot-health-insurance
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get your API key from https://platform.openai.com/api-keys
```

Or set directly in your shell:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Start Backend
```bash
# Using Maven
mvn clean install
mvn spring-boot:run

# OR using Gradle
./gradlew clean build
./gradlew bootRun
```

Backend will start at `http://localhost:8080`

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend will start at `http://localhost:3001`

### 5. Test the System
```bash
# Run the test script
./test-enhanced-system.sh
```

## 📱 Using the Enhanced Features

### Voice Input
1. Click the microphone icon in the chat input
2. Speak your question clearly
3. Click again to stop recording
4. Your speech will be converted to text automatically

### Citations
1. After receiving a response, look for the "Show X sources" button
2. Click to expand and see the source documents
3. Each citation includes the source title and relevant snippet

### Analytics Dashboard
1. Click the "Analytics" button in the header
2. View real-time metrics including:
   - Query volume and trends
   - Response times
   - Popular topics
   - Recent queries

### Quick Actions
Use the pre-configured buttons for common queries:
- 📅 Schedule Appointment
- 🏥 Available Services  
- 🛡️ Insurance Info
- 📍 Location & Hours
- 🧠 Mental Health
- ❤️ Preventive Care

## 🔧 Advanced Configuration

### Enable Persistence
```bash
# Start Chroma vector database
docker run -p 8000:8000 chromadb/chroma

# Start Redis cache
docker run -p 6379:6379 redis:alpine
```

### Production Deployment
```bash
# Build for production
cd frontend
npm run build

# Backend with production profile
java -jar -Dspring.profiles.active=prod target/chatbot.jar
```

## 🎯 Key API Endpoints

### Chat with Citations
```bash
POST http://localhost:8080/api/v2/chat
{
  "message": "What mental health services are available?"
}
```

### Upload Documents
```bash
POST http://localhost:8080/api/v1/documents/upload
Form-data: file=<your-document.pdf>
```

### View Analytics
```bash
GET http://localhost:8080/api/v1/metrics/dashboard
```

## 🐛 Troubleshooting

### Backend Issues
- Ensure Java 17 or 21 is installed: `java -version`
- Check port 8080 is free: `lsof -i :8080`
- Verify API keys are set correctly

### Frontend Issues
- Clear Next.js cache: `rm -rf .next`
- Check Node version: `node --version` (should be 18+)
- Ensure backend is running first

### Voice Input Not Working
- Voice input requires HTTPS in production
- Check browser permissions for microphone
- Try Chrome/Edge for best compatibility

## 📈 Performance Tips
- The first query may be slower due to model loading
- Subsequent queries benefit from caching
- Use Chroma for persistent vector storage
- Enable Redis for production caching

## 🔐 Security Notes
- Never commit API keys to version control
- Use environment variables for sensitive data
- Enable CORS only for trusted domains in production
- Implement rate limiting for public deployments

## 📚 Additional Resources
- [Full Documentation](PRODUCTION_ENHANCEMENTS_V2.md)
- [API Reference](src/main/resources/static/api-docs.html)
- [Contributing Guide](CONTRIBUTING.md)

## 🎉 Ready to Go!
Your enhanced chatbot is now ready. Visit http://localhost:3001 and start asking questions about CMU Health Services!

---
Made with ❤️ by Siva Komaragiri for the CMU community