# 🏥 CMU Health Services Chatbot - System Running Summary

## ✅ Current Status

Both services are now running locally with comprehensive logging enabled.

### Backend Service
- **Status**: ✅ Running
- **Port**: 8080
- **API Key**: OpenAI API key configured
- **Knowledge Base**: 1,113 segments loaded from CMU health data
- **Log File**: `logs/backend_manual.log`
- **Process**: Java Spring Boot application

### Frontend Service
- **Status**: ✅ Running
- **Port**: 3001
- **UI**: Modern healthcare chatbot interface
- **Features**: Voice input, real-time status, citations
- **Log File**: `logs/frontend_manual.log`
- **Process**: Next.js development server

## 🌐 Access Points

### Main Application
- **URL**: http://localhost:3001
- **Features**:
  - 🎤 Voice input (click microphone icon)
  - 💬 AI-powered chat responses
  - 📚 Citation display
  - 🎨 Dark/light theme toggle
  - ⚡ Real-time connection status

### Analytics Dashboard
- **URL**: http://localhost:3001/analytics
- **Features**:
  - 📊 Query volume metrics
  - ⏱️ Response time tracking
  - 📈 Usage patterns
  - 🔍 Recent queries

### API Endpoints
- **Health Check**: http://localhost:8080/api/v1/health
- **Basic Chat**: POST http://localhost:8080/api/v1/chat
- **Document Upload**: POST http://localhost:8080/api/v1/documents/upload

## 📊 Log Monitoring

### View Live Logs
```bash
# All logs with color coding
./live-monitor.sh

# Backend logs only
tail -f logs/backend_manual.log

# Frontend logs only
tail -f logs/frontend_manual.log
```

### Log Analysis Tools
```bash
# Interactive log viewer
./view-logs.sh

# System status dashboard
./monitor-system.sh

# Quick status check
./system-status.sh
```

## 🧪 Testing the System

### Test Chat via API
```bash
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What services are available?"}'
```

### Test via Frontend
1. Open http://localhost:3001
2. Type or speak your question
3. View AI response with citations

## 📁 Log Files Location

All logs are stored in the `logs/` directory:
- `backend_manual.log` - Backend application logs
- `frontend_manual.log` - Frontend application logs
- Timestamped logs from previous runs

## 🛠️ Troubleshooting

### If services stop:
```bash
# Check what's running
ps aux | grep -E "gradlew|next"

# Restart backend
export OPENAI_API_KEY="your-key"
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
./gradlew bootRun > logs/backend_manual.log 2>&1 &

# Restart frontend
npm run dev --prefix frontend > logs/frontend_manual.log 2>&1 &
```

### Common Issues:
- **Port 8080 in use**: Kill existing process with `lsof -ti :8080 | xargs kill -9`
- **Port 3001 in use**: Kill existing process with `lsof -ti :3001 | xargs kill -9`
- **API key issues**: Check logs for "demo mode" messages

## 🎯 What to Test

1. **Voice Input**: Click microphone and speak "What are your hours?"
2. **Quick Actions**: Use the sidebar buttons for common queries
3. **Citations**: Ask detailed questions to see source references
4. **Analytics**: Visit the dashboard to see usage metrics
5. **Document Upload**: Upload a health-related PDF or text file

## 📝 Current Configuration

- **LLM Provider**: OpenAI (GPT-3.5-turbo)
- **Embedding Model**: all-MiniLM-L6-v2
- **Vector Store**: In-memory (non-persistent)
- **Chunk Size**: 600 characters with 100 overlap
- **Max Documents**: 5 per query

---

The system is fully operational and ready for testing! All interactions are being logged for monitoring and debugging purposes.