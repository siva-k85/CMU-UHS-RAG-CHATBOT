#!/bin/bash

# Live System Monitor with Real-time Logs
echo "🚀 CMU Health Services Chatbot - Live Monitor"
echo "============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Display system info
echo -e "${BLUE}System Information:${NC}"
echo "  Backend URL:  http://localhost:8080"
echo "  Frontend URL: http://localhost:3001"
echo "  Analytics:    http://localhost:3001/analytics"
echo ""

echo -e "${BLUE}Log Files:${NC}"
echo "  Backend:  logs/backend_manual.log"
echo "  Frontend: logs/frontend_manual.log"
echo ""

echo -e "${GREEN}Services are running. Monitoring logs...${NC}"
echo "============================================="
echo ""

# Monitor both logs simultaneously
echo -e "${CYAN}[Press Ctrl+C to stop monitoring]${NC}"
echo ""

# Use tail to follow both files with labels
tail -f logs/backend_manual.log logs/frontend_manual.log 2>/dev/null | while IFS= read -r line; do
    # Add color coding based on content
    if echo "$line" | grep -q "==> logs/backend_manual.log <=="; then
        echo -e "\n${BLUE}[BACKEND]${NC}"
    elif echo "$line" | grep -q "==> logs/frontend_manual.log <=="; then
        echo -e "\n${CYAN}[FRONTEND]${NC}"
    elif echo "$line" | grep -q "ERROR\|Exception"; then
        echo -e "${RED}[ERROR]${NC} $line"
    elif echo "$line" | grep -q "WARN"; then
        echo -e "${YELLOW}[WARN]${NC} $line"
    elif echo "$line" | grep -q "Processing user message\|ChatbotService"; then
        echo -e "${GREEN}[CHAT]${NC} $line"
    elif echo "$line" | grep -q "INFO.*Started\|Ready in"; then
        echo -e "${GREEN}[READY]${NC} $line"
    elif echo "$line" | grep -q "GET\|POST"; then
        echo -e "${CYAN}[HTTP]${NC} $line"
    else
        echo "$line"
    fi
done