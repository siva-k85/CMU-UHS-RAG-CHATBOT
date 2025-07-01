#!/bin/bash

echo "Testing CMU UHS RAG Chatbot..."
echo ""

# Test health endpoint
echo "1. Testing health endpoint:"
curl -s http://localhost:8080/api/v1/health | jq . || echo "Health check failed"
echo ""

# Test chat endpoint (without auth in dev mode)
echo "2. Testing chat endpoint:"
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What are the health services hours?"}' \
  | jq . || echo "Chat endpoint failed"
echo ""

# Test actuator health
echo "3. Testing actuator health:"
curl -s http://localhost:8080/actuator/health | jq . || echo "Actuator health failed"
echo ""

echo "Test complete!"