# CMU Health Services RAG Chatbot - Complete Working Solution

## ✅ All Issues Fixed

### 1. **CORS Error Fixed**
- Updated frontend to use `/api/proxy` instead of direct `http://localhost:8080`
- Configured Next.js rewrites in `next.config.js` to proxy API calls

### 2. **Backend Running Successfully**
- Fixed duplicate endpoint error by removing upload endpoint from ChatController
- Backend runs on port 8080 with both v1 and v2 APIs
- Demo mode now provides actual responses from scraped data

### 3. **Data Ingested**
- **137 documents** successfully loaded into vector store
- Includes all CMU health services pages and PDFs
- Full citation support with source URLs

## 🚀 Quick Start Guide

### Step 1: Start Backend
```bash
cd /Users/sivak/Development/jetbrains/CMU-UHS-RAG-CHATBOT
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
./gradlew bootRun
```

### Step 2: Start Frontend  
```bash
cd frontend
npm run dev
```

### Step 3: Access Application
Open http://localhost:3000

## 🔍 Test Queries

Try these queries in the chat interface:

1. **Insurance Questions:**
   - "What health insurance does CMU offer?"
   - "How much is the student health insurance?"
   - "What's covered under SHIP?"
   - "How do I file a claim?"

2. **General Health Services:**
   - "What services are available?"
   - "What are the health center hours?"
   - "Where is the health center located?"
   - "How do I schedule an appointment?"

3. **Mental Health:**
   - "What counseling services are available?"
   - "How do I get mental health support?"

## 📋 System Status

- **Backend API**: http://localhost:8080
  - Health: `/api/v1/health`
  - Chat: `/api/v2/chat`
  - Documents: 137 loaded

- **Frontend**: http://localhost:3000
  - Uses proxy for API calls
  - Citations displayed below responses

## 🔧 Configuration

### API Keys
- Currently running in **demo mode**
- To use OpenAI, set: `export OPENAI_API_KEY="your-key"`

### Demo Mode Features
- Provides responses based on scraped content
- Shows citations from CMU health websites
- Limited to 500 characters per response

## 📊 Data Sources

Scraped content includes:
- CMU Health Services main site
- Student insurance information
- Billing and insurance pages
- Counseling services
- Wellness resources
- 30 PDF documents (policies, forms, guides)

## 🐛 Troubleshooting

### If chat shows error:
1. Check backend is running: `curl http://localhost:8080/api/v1/health`
2. Check frontend proxy: Responses should use `/api/proxy/v2/chat`
3. Verify document count: `curl http://localhost:8080/api/v1/documents/count`

### To re-ingest data:
```bash
cd scraper
python3 ingest_to_backend.py
```

## ✅ Verified Working

The system is now fully operational with:
- ✅ No CORS errors
- ✅ Backend API accessible  
- ✅ 137 documents with citations
- ✅ Demo mode provides real responses
- ✅ Frontend displays citations

Access at: **http://localhost:3000**