# CMU Health Services RAG Chatbot - Working Demo

## 🎯 System Overview

The CMU Health Services RAG Chatbot is now fully operational with:

### 1. **Web Scraping System**
- Automated scraper for CMU health websites
- Extracts structured data (hours, phone numbers, services)
- Preserves source URLs for citations
- Exports to multiple formats (JSON, Markdown)

### 2. **Enhanced Backend (Spring Boot)**
- RAG system with LangChain4j integration
- Citation tracking for all responses
- Document ingestion from multiple sources
- RESTful API with enhanced endpoints

### 3. **Beautiful Frontend (Next.js)**
- Modern healthcare-themed UI
- Real-time chat interface
- Citation display with source links
- Quick action buttons
- Document upload functionality

## 📸 Visual Demo

### Main Chat Interface
```
┌─────────────────────────────────────────────────────────────┐
│  ❤️ CMU Health Services        📞 412-268-2157  🕐 Mon-Fri  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────────────────────────────┐ │
│  │ Quick Actions│    │  🤖 Health Assistant                │ │
│  │             │    │                                      │ │
│  │ 📅 Schedule │    │  👤 User: What are the hours?       │ │
│  │ ❤️ Services │    │                                      │ │
│  │ 📄 Insurance│    │  🤖 Assistant: CMU Health Services  │ │
│  │ 📍 Location │    │     is open Monday-Friday from      │ │
│  └─────────────┘    │     8:30 AM to 5:00 PM.            │ │
│                     │                                      │ │
│  ┌─────────────┐    │     📚 Sources:                     │ │
│  │ Contact Info│    │     • CMU Health Services Info      │ │
│  │             │    │       URL: cmu.edu/health-services  │ │
│  │ 📍 1060     │    │       "Regular hours are..."        │ │
│  │ Morewood Ave│    │                                      │ │
│  │             │    │  [Type your question...]      [Send] │ │
│  └─────────────┘    └─────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔍 How Citations Work

1. **User asks a question**
   ```
   "What mental health services are available?"
   ```

2. **System searches knowledge base**
   - Finds relevant documents from scraped CMU websites
   - Retrieves metadata including source URLs

3. **Response with citations**
   ```json
   {
     "response": "CMU offers comprehensive mental health services through CAPS...",
     "citations": [
       {
         "title": "Counseling & Psychological Services",
         "url": "https://www.cmu.edu/counseling/",
         "snippet": "Individual counseling, group therapy, crisis intervention..."
       }
     ]
   }
   ```

4. **Frontend displays citations**
   - Shows source links below the answer
   - Users can click to verify information

## 🚀 Running the System

### Start Backend:
```bash
export OPENAI_API_KEY="your-key"
./gradlew bootRun
```

### Start Frontend:
```bash
cd frontend
npm run dev
```

### Run Web Scraper:
```bash
cd scraper
python3 run_scraper_and_ingest.py
```

## 📊 Live Features

- ✅ **Real-time chat** with CMU health information
- ✅ **Source citations** for every answer
- ✅ **Web scraping** of official CMU health pages
- ✅ **Document upload** to expand knowledge base
- ✅ **Quick actions** for common questions
- ✅ **Dark mode** support
- ✅ **Mobile responsive** design

## 🎨 Technology Stack

- **Backend**: Spring Boot 3.2.5, Java 17, LangChain4j
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS
- **Scraper**: Python, BeautifulSoup4, Requests
- **Vector Store**: In-memory with semantic search
- **LLM**: OpenAI GPT-3.5-turbo

## 📱 Access Points

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8080/api/v1/chat
- **Enhanced API**: http://localhost:8080/api/v2/chat (with citations)
- **Health Check**: http://localhost:8080/api/v1/health

The system is fully operational and ready for student use!