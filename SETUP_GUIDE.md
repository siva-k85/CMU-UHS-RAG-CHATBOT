# CMU UHS RAG Chatbot Setup Guide

## Project Overview
This is a Retrieval-Augmented Generation (RAG) chatbot designed for Carnegie Mellon University Health Services. It uses:
- Spring Boot for the backend REST API
- LangChain4j for RAG implementation
- OpenAI for LLM responses
- In-memory vector storage for document embeddings

## Current Issue
Your system has Java 24 installed, but Gradle requires Java 17 or 21 to build Spring Boot applications.

## Setup Instructions

### 1. Install Java 17
```bash
brew install openjdk@17
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
```

### 2. Set Java Environment
```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
export PATH=$JAVA_HOME/bin:$PATH
```

### 3. Verify Java Version
```bash
java -version  # Should show version 17
```

### 4. Run the Application
```bash
./gradlew bootRun
```

## Alternative: Using IntelliJ IDEA
Since you're using IntelliJ IDEA:
1. Open the project in IntelliJ
2. Go to File → Project Structure → Project
3. Set Project SDK to Java 17 (download if needed)
4. Go to File → Project Structure → Modules
5. Set Language Level to 17
6. Right-click on `RagChatbotApplication.java` and select "Run"

## Features
- **Chat Interface**: Available at http://localhost:8080
- **Document Upload**: Upload PDFs, TXT, or MD files through the web interface
- **Auto-ingestion**: Automatically loads documents from the `data/` directory on startup
- **REST API**: 
  - POST `/api/v1/chat` - Send chat messages
  - POST `/api/v1/documents/upload` - Upload documents
  - GET `/api/v1/health` - Health check

## Sample CMU UHS Data
The `data/cmu-uhs-info.md` file contains sample information about:
- Contact information and hours
- Services offered (primary care, mental health, etc.)
- Appointment scheduling
- Insurance information
- Special programs

## Troubleshooting
- If you see "Unsupported class file major version 68", you're using Java 24 instead of Java 17
- If the OpenAI API fails, check your API key is valid
- For build issues, try `./gradlew clean build --refresh-dependencies`

## Next Steps
1. Add more CMU UHS documents to the `data/` directory
2. Customize the chatbot prompt in `ChatbotService.java`
3. Consider switching to a persistent vector database like Chroma or Pinecone
4. Add authentication for production use