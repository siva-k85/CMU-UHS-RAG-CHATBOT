#!/bin/bash

echo "Testing CMU UHS RAG Chatbot..."
echo "=============================="
echo ""

# Check backend health
echo "1. Backend Health Check:"
curl -s http://localhost:8080/api/v1/health || echo "Backend not responding"
echo -e "\n"

# Test chat endpoint
echo "2. Testing Chat Endpoint:"
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What are the health center hours?"}' \
  -s | jq . || echo "Chat endpoint failed"
echo -e "\n"

# Check frontend
echo "3. Frontend Status:"
curl -s http://localhost:3000 > /dev/null && echo "Frontend is running on http://localhost:3000" || echo "Frontend not responding"
echo ""

echo "=================================="
echo "If both services are running:"
echo "Visit http://localhost:3000 in your browser"
echo "=================================="