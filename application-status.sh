#!/bin/bash

echo "==================================="
echo "CMU UHS RAG Chatbot - Status Check"
echo "==================================="
echo ""

# Check if application is running
if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    echo "✅ Application Status: RUNNING"
    echo "   URL: http://localhost:8080"
else
    echo "❌ Application Status: NOT RUNNING"
    exit 1
fi

echo ""
echo "Available Endpoints:"
echo "-------------------"
echo "📍 Health Check: http://localhost:8080/api/v1/health"
echo "💬 Chat API: http://localhost:8080/api/v1/chat"
echo ""

echo "Test Examples:"
echo "--------------"
echo ""
echo "1. Health Check:"
echo "   curl http://localhost:8080/api/v1/health"
echo ""
echo "2. Chat Query:"
echo "   curl -X POST http://localhost:8080/api/v1/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\":\"What services are available?\"}'"
echo ""

echo "Current Configuration:"
echo "---------------------"
echo "- Profile: dev (security disabled)"
echo "- Java Version: 17"
echo "- Vector Store: In-memory"
echo "- LLM: Demo mode"
echo ""
echo "==================================="