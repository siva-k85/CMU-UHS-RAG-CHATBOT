#!/bin/bash

# Status check for Enhanced CMU Health Services Chatbot

echo "🔍 CMU Health Services Chatbot Status Check"
echo "=========================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Backend
echo -e "\n📡 Backend Status:"
if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend is running on port 8080"
    # Test enhanced endpoint
    if curl -s http://localhost:8080/api/v2/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Enhanced API endpoints available"
    fi
else
    echo -e "${RED}✗${NC} Backend is not running"
    echo "  Start with: mvn spring-boot:run"
fi

# Check Frontend
echo -e "\n💻 Frontend Status:"
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend is running on port 3001"
    echo "  URL: http://localhost:3001"
else
    echo -e "${RED}✗${NC} Frontend is not running"
    echo "  Start with: cd frontend && npm run dev"
fi

# Check Process
echo -e "\n🔧 Running Processes:"
if ps aux | grep -v grep | grep -q "spring-boot:run"; then
    echo -e "${GREEN}✓${NC} Spring Boot process detected"
fi
if ps aux | grep -v grep | grep -q "next dev.*3001"; then
    echo -e "${GREEN}✓${NC} Next.js dev server detected on port 3001"
fi

# Quick Health Test
echo -e "\n🏥 Quick Health Test:"
response=$(curl -s -X POST http://localhost:8080/api/v2/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}' 2>/dev/null || echo "failed")

if [[ "$response" == *"response"* ]]; then
    echo -e "${GREEN}✓${NC} Chat API is responding"
else
    echo -e "${YELLOW}⚠️${NC} Chat API may not be fully initialized"
fi

echo -e "\n=========================================="
echo -e "${BLUE}Ready to chat?${NC} Visit http://localhost:3001"
echo -e "${BLUE}View analytics?${NC} Visit http://localhost:3001/analytics"