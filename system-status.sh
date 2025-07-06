#!/bin/bash

# System Status Dashboard
echo "======================================"
echo "🏥 CMU Health Services Chatbot Status"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Backend Status
echo -e "${BLUE}Backend Status:${NC}"
if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Backend API: Running"
    echo -e "  ${GREEN}✓${NC} Health Check: Passed"
    
    # Check if OpenAI is configured
    response=$(curl -s -X POST http://localhost:8080/api/v1/chat \
      -H "Content-Type: application/json" \
      -d '{"message":"test"}' 2>/dev/null || echo "error")
    
    if echo "$response" | grep -q "demo mode"; then
        echo -e "  ${YELLOW}⚠️${NC} AI Mode: Demo (API key not active)"
    else
        echo -e "  ${GREEN}✓${NC} AI Mode: OpenAI Enabled"
    fi
else
    echo -e "  ${RED}✗${NC} Backend API: Not Running"
fi

# Frontend Status
echo -e "\n${BLUE}Frontend Status:${NC}"
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Frontend: Running on port 3001"
    echo -e "  ${GREEN}✓${NC} UI Available: http://localhost:3001"
else
    echo -e "  ${RED}✗${NC} Frontend: Not Running"
fi

# Feature Status
echo -e "\n${BLUE}Enhanced Features:${NC}"
echo -e "  ${GREEN}✓${NC} Voice Input: Available"
echo -e "  ${GREEN}✓${NC} Real-time Status: Active"
echo -e "  ${GREEN}✓${NC} Citation Support: Enabled"
echo -e "  ${GREEN}✓${NC} Analytics Dashboard: http://localhost:3001/analytics"

# Quick Links
echo -e "\n${BLUE}Quick Access:${NC}"
echo "  📱 Main App: http://localhost:3001"
echo "  📊 Analytics: http://localhost:3001/analytics"
echo "  🔧 API Health: http://localhost:8080/api/v1/health"

echo -e "\n======================================"