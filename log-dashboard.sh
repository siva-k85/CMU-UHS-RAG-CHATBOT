#!/bin/bash

# Log Dashboard for CMU Health Services Chatbot
clear
echo "📊 CMU Health Services Chatbot - Live Dashboard"
echo "=============================================="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Find latest log files
LATEST_BACKEND=$(ls -t logs/backend_*.log 2>/dev/null | head -1)
LATEST_FRONTEND=$(ls -t logs/frontend_*.log 2>/dev/null | head -1)
LATEST_SYSTEM=$(ls -t logs/system_*.log 2>/dev/null | head -1)

# Function to show dashboard
show_dashboard() {
    while true; do
        clear
        echo "📊 CMU Health Services Chatbot - Live Dashboard"
        echo "=============================================="
        echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        
        # Service Status
        echo -e "${BLUE}Service Status:${NC}"
        if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
            echo -e "  Backend:  ${GREEN}● Running${NC}"
        else
            echo -e "  Backend:  ${RED}● Down${NC}"
        fi
        
        if curl -s http://localhost:3001 > /dev/null 2>&1; then
            echo -e "  Frontend: ${GREEN}● Running${NC}"
        else
            echo -e "  Frontend: ${RED}● Down${NC}"
        fi
        echo ""
        
        # Statistics
        echo -e "${BLUE}Statistics:${NC}"
        if [[ -f "$LATEST_BACKEND" ]]; then
            CHAT_COUNT=$(grep -c "Processing user message\|chat request" "$LATEST_BACKEND" 2>/dev/null || echo 0)
            ERROR_COUNT=$(grep -ci "error\|exception" "$LATEST_BACKEND" 2>/dev/null || echo 0)
            echo "  Chat Requests: $CHAT_COUNT"
            echo "  Errors: $ERROR_COUNT"
        fi
        echo ""
        
        # Recent Activity
        echo -e "${BLUE}Recent Activity:${NC}"
        if [[ -f "$LATEST_BACKEND" ]]; then
            tail -n 5 "$LATEST_BACKEND" 2>/dev/null | grep -E "Processing user message|Generated response|ERROR" | while IFS= read -r line; do
                if echo "$line" | grep -q "ERROR"; then
                    echo -e "  ${RED}[ERROR]${NC} ${line:0:60}..."
                elif echo "$line" | grep -q "Processing user message"; then
                    echo -e "  ${GREEN}[CHAT]${NC} New query received"
                elif echo "$line" | grep -q "Generated response"; then
                    echo -e "  ${CYAN}[RESP]${NC} Response generated"
                fi
            done
        fi
        echo ""
        
        # Recent Frontend Activity
        echo -e "${BLUE}Frontend Activity:${NC}"
        if [[ -f "$LATEST_FRONTEND" ]]; then
            tail -n 3 "$LATEST_FRONTEND" 2>/dev/null | while IFS= read -r line; do
                if echo "$line" | grep -q "compiled"; then
                    echo -e "  ${GREEN}[BUILD]${NC} ${line:0:60}..."
                else
                    echo "  ${line:0:70}..."
                fi
            done
        fi
        echo ""
        
        echo "=============================================="
        echo -e "${YELLOW}Press Ctrl+C to exit${NC} | Refreshing every 5 seconds"
        
        sleep 5
    done
}

# Run dashboard
show_dashboard