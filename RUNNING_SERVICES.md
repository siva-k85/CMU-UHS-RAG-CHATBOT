# 🚀 CMU UHS RAG Chatbot - Running Services

Both frontend and backend services are now running!

## 🔗 Access Links

### Frontend (Main Application)
**URL: http://localhost:3000**
- Full chat interface with modern UI
- Real-time chat with typing indicators
- Citation display for responses
- Dark mode support
- Voice input capability

### Backend API
**URL: http://localhost:8080**
- Health Check: http://localhost:8080/api/v1/health
- Chat API: http://localhost:8080/api/v1/chat
- Actuator: http://localhost:8080/actuator/health

## ✅ Service Status

### Backend (Spring Boot)
- **Port**: 8080
- **Status**: ✅ Running
- **Profile**: dev (security disabled)
- **Documents Loaded**: 1,113 segments
- **Vector Store**: In-memory
- **Features**:
  - WebSocket support for streaming
  - Health monitoring endpoints
  - CORS enabled for frontend

### Frontend (Next.js)
- **Port**: 3000
- **Status**: ✅ Running
- **Features**:
  - Modern React UI
  - Real-time chat interface
  - Voice input support
  - Dark/Light theme toggle
  - Citation display
  - Responsive design

## 🧪 Test the Application

1. **Open the Chat Interface**:
   Visit http://localhost:3000 in your browser

2. **Try These Questions**:
   - "What are the health center hours?"
   - "How do I make an appointment?"
   - "What mental health services are available?"
   - "Tell me about student insurance"
   - "What immunizations do I need?"

3. **Test Voice Input**:
   Click the microphone icon to use voice input

4. **Check Citations**:
   Responses include source citations from the knowledge base

## 📊 Current Configuration

- **LLM Mode**: Demo (no API key required)
- **Security**: Disabled (dev profile)
- **CORS**: Enabled for all origins
- **WebSocket**: Active for real-time updates
- **Cache**: Simple in-memory

## 🛑 To Stop Services

```bash
# Stop frontend
pkill -f "npm run dev"

# Stop backend
pkill -f "gradle.*bootRun"
```

The application is fully functional and ready for testing!