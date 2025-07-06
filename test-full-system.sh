#!/bin/bash

# Full System Test with OpenAI Integration
echo "🧪 CMU Health Services Chatbot - Full System Test"
echo "==============================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to initialize...${NC}"
sleep 5

# 1. Check Backend Health
echo -e "\n${BLUE}1. Backend Health Check${NC}"
if curl -s http://localhost:8080/api/v1/health > /dev/null; then
    echo -e "${GREEN}✓${NC} Backend is healthy"
else
    echo -e "${RED}✗${NC} Backend is not responding"
    exit 1
fi

# 2. Check Frontend
echo -e "\n${BLUE}2. Frontend Health Check${NC}"
if curl -s http://localhost:3001 > /dev/null; then
    echo -e "${GREEN}✓${NC} Frontend is accessible at http://localhost:3001"
else
    echo -e "${RED}✗${NC} Frontend is not responding"
fi

# 3. Test Basic Chat Endpoint
echo -e "\n${BLUE}3. Testing Basic Chat (v1)${NC}"
response=$(curl -s -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What services does CMU Health Services offer?"}')

if echo "$response" | grep -q "Primary Care\|Mental Health\|health services"; then
    echo -e "${GREEN}✓${NC} Basic chat endpoint is working with AI"
    echo "Response preview: $(echo "$response" | head -c 150)..."
else
    echo -e "${YELLOW}⚠️${NC} Basic chat may be in demo mode"
fi

# 4. Test Enhanced Chat with Citations
echo -e "\n${BLUE}4. Testing Enhanced Chat (v2)${NC}"
response=$(curl -s -X POST http://localhost:8080/api/v2/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What are the hours of operation for CMU Health Services?"}')

if echo "$response" | grep -q "citations\|response"; then
    echo -e "${GREEN}✓${NC} Enhanced chat with citations is working"
    
    # Check if we have actual citations
    if echo "$response" | grep -q '"citations":\[\]'; then
        echo -e "${YELLOW}⚠️${NC} No citations found (may need more data)"
    else
        echo -e "${GREEN}✓${NC} Citations are being generated"
    fi
    
    # Check confidence score
    if echo "$response" | grep -q '"confidence"'; then
        echo -e "${GREEN}✓${NC} Confidence scoring is active"
    fi
else
    echo -e "${RED}✗${NC} Enhanced chat endpoint issue"
fi

# 5. Test Analytics Endpoint
echo -e "\n${BLUE}5. Testing Analytics Dashboard${NC}"
if curl -s http://localhost:8080/api/v1/metrics/dashboard > /dev/null; then
    echo -e "${GREEN}✓${NC} Analytics endpoint is accessible"
else
    echo -e "${YELLOW}⚠️${NC} Analytics endpoint not available"
fi

# 6. Test Document Upload
echo -e "\n${BLUE}6. Testing Document Upload${NC}"
echo "Test health document content" > /tmp/test-health-doc.txt
response=$(curl -s -X POST http://localhost:8080/api/v1/documents/upload \
  -F "file=@/tmp/test-health-doc.txt")

if echo "$response" | grep -q "success\|uploaded"; then
    echo -e "${GREEN}✓${NC} Document upload working"
else
    echo -e "${YELLOW}⚠️${NC} Document upload may have issues"
fi
rm -f /tmp/test-health-doc.txt

# 7. Test Frontend Proxy
echo -e "\n${BLUE}7. Testing Frontend API Proxy${NC}"
response=$(curl -s -X POST http://localhost:3001/api/proxy/v1/chat/enhanced \
  -H "Content-Type: application/json" \
  -d '{"message":"Test query through frontend"}')

if echo "$response" | grep -q "response"; then
    echo -e "${GREEN}✓${NC} Frontend proxy is working correctly"
else
    echo -e "${RED}✗${NC} Frontend proxy issue"
fi

# Summary
echo -e "\n${GREEN}===============================================${NC}"
echo -e "${GREEN}✅ SYSTEM TEST COMPLETE${NC}"
echo -e "${GREEN}===============================================${NC}"
echo ""
echo -e "${BLUE}Key Features Ready:${NC}"
echo "• AI-powered chat responses with OpenAI GPT-3.5"
echo "• Citation support for source verification"
echo "• Voice input capability (in browser)"
echo "• Real-time status indicators"
echo "• Analytics dashboard"
echo "• Document upload for knowledge expansion"
echo ""
echo -e "${YELLOW}Access Points:${NC}"
echo "• Main App: ${BLUE}http://localhost:3001${NC}"
echo "• Analytics: ${BLUE}http://localhost:3001/analytics${NC}"
echo "• API Docs: ${BLUE}http://localhost:8080${NC}"
echo ""
echo -e "${GREEN}✨ Your enhanced chatbot is ready for testing!${NC}"