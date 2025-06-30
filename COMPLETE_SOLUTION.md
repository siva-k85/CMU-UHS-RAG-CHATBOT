# CMU Health Services RAG Chatbot - Complete Solution

## 🎉 System Overview

The CMU Health Services RAG Chatbot is now fully operational with:

1. **228 pages scraped** from CMU health websites
2. **30 PDFs extracted** including insurance documents
3. **174 insurance-related documents** identified and categorized
4. **Complete citation support** showing source URLs for every answer

## 📊 Scraping Results

- **Total Pages Scraped**: 228
- **PDF Documents**: 30 (including insurance policies, forms, guides)
- **Insurance-Specific Content**: 174 documents
- **Data Format**: XML with full metadata preservation

Key insurance PDFs captured:
- Student Health Insurance Plan (SHIP) books and guides
- Medical, dental, and vision plan details
- Coverage grids and benefit summaries
- Claim forms and procedures
- Travel insurance information

## 🚀 Running the Complete System

### Quick Start (All-in-One)

```bash
cd /Users/sivak/Development/jetbrains/CMU-UHS-RAG-CHATBOT
./run_complete_system.sh
```

This script will:
1. Start the Spring Boot backend (port 8080)
2. Start the Next.js frontend (port 3000)
3. Ingest all scraped data into the vector store
4. Display system status and document count

### Manual Steps

1. **Backend**:
   ```bash
   export OPENAI_API_KEY="your-key"  # Optional
   ./gradlew bootRun
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Ingest Data**:
   ```bash
   cd scraper
   python3 ingest_to_backend.py
   ```

## 🔍 Testing the System

Access the chatbot at: **http://localhost:3000**

### Sample Queries to Test:

**Insurance Questions:**
- "What health insurance plans does CMU offer?"
- "How much does the student health insurance cost?"
- "What is covered under the CMU student insurance?"
- "How do I file an insurance claim at CMU?"
- "Does CMU insurance cover mental health services?"
- "What is the deductible for the student health plan?"

**General Health Services:**
- "What are the health center hours?"
- "Where is the CMU health center located?"
- "How do I schedule an appointment?"
- "What services are available at the health center?"
- "Is there a pharmacy on campus?"

**Mental Health:**
- "What counseling services are available?"
- "How do I access mental health support at CMU?"
- "Are there support groups available?"

## 📁 Data Structure

```
scraped_data_xml/
├── summary.json           # Scraping statistics
├── pages/                 # 51 general HTML pages
├── insurance/             # 174 insurance-related documents
├── pdfs/                  # 30 downloaded PDFs
└── scraped_data_for_rag.json  # Processed data (214 documents)
```

## 🔧 System Architecture

1. **Web Scraper** (Python)
   - BeautifulSoup for HTML parsing
   - PyPDF2/pdfplumber for PDF extraction
   - XML export with metadata preservation

2. **Backend** (Spring Boot)
   - LangChain4j for RAG implementation
   - In-memory vector store
   - RESTful API with citation support
   - Batch document ingestion endpoint

3. **Frontend** (Next.js)
   - Modern chat interface
   - Real-time responses
   - Citation display with source links
   - Mobile responsive design

## 📈 Key Features

- **Comprehensive Coverage**: All CMU health services information
- **PDF Intelligence**: Extracts tables, forms, and structured data
- **Citation Tracking**: Every answer includes source references
- **Insurance Focus**: Special handling for insurance documents
- **Batch Processing**: Efficient ingestion of 200+ documents

## 🛠️ Troubleshooting

**Backend not starting:**
```bash
# Check Java version (needs 17)
java -version
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
```

**Frontend issues:**
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

**No documents showing:**
```bash
# Re-run ingestion
cd scraper
python3 ingest_to_backend.py
```

## 📊 API Endpoints

- **Chat**: `POST http://localhost:8080/api/v1/chat`
- **Chat with Citations**: `POST http://localhost:8080/api/v2/chat`
- **Document Count**: `GET http://localhost:8080/api/v1/documents/count`
- **Health Check**: `GET http://localhost:8080/api/v1/health`

## ✅ Verification

The system is working correctly when:
1. Backend shows: "Vector store initialized"
2. Document count shows: 214+ documents
3. Frontend loads at http://localhost:3000
4. Queries return answers with citations

## 🎯 Next Steps

1. **Production Deployment**: Use the GCP deployment guide
2. **Add Authentication**: Implement user sessions
3. **Enhanced UI**: Add document upload in frontend
4. **Analytics**: Track popular queries
5. **Continuous Updates**: Schedule regular web scraping

The complete RAG system is now operational with all CMU health and insurance information embedded!