#!/bin/bash

# Comprehensive System Monitor with Logs
echo "🔍 CMU Health Services Chatbot - System Monitor"
echo "=============================================="

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Create logs directory if needed
mkdir -p logs

# Check current process status
echo -e "\n${BLUE}Current Process Status:${NC}"
echo "------------------------------"

# Check backend processes
BACKEND_PROCS=$(ps aux | grep -E "java.*RagChatbot|gradlew.*bootRun" | grep -v grep)
if [[ -n "$BACKEND_PROCS" ]]; then
    echo -e "${GREEN}✓ Backend processes found:${NC}"
    echo "$BACKEND_PROCS" | awk '{print "  PID:", $2, "CMD:", substr($0, index($0,$11))}'
else
    echo -e "${RED}✗ No backend processes running${NC}"
fi

# Check frontend processes
FRONTEND_PROCS=$(ps aux | grep "next dev.*3001" | grep -v grep)
if [[ -n "$FRONTEND_PROCS" ]]; then
    echo -e "${GREEN}✓ Frontend processes found:${NC}"
    echo "$FRONTEND_PROCS" | awk '{print "  PID:", $2, "CMD:", substr($0, index($0,$11))}'
else
    echo -e "${RED}✗ No frontend processes running${NC}"
fi

# Check service endpoints
echo -e "\n${BLUE}Service Endpoints:${NC}"
echo "------------------------------"

# Backend health check
echo -n "Backend (8080): "
if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Responding${NC}"
    
    # Test chat capability
    echo -n "  Chat API: "
    CHAT_RESPONSE=$(curl -s -X POST http://localhost:8080/api/v1/chat \
      -H "Content-Type: application/json" \
      -d '{"message":"test"}' 2>/dev/null)
    
    if [[ -n "$CHAT_RESPONSE" ]]; then
        if echo "$CHAT_RESPONSE" | grep -q "demo mode"; then
            echo -e "${YELLOW}Demo Mode${NC}"
        else
            echo -e "${GREEN}✓ OpenAI Active${NC}"
        fi
    else
        echo -e "${RED}✗ Not responding${NC}"
    fi
else
    echo -e "${RED}✗ Not responding${NC}"
fi

# Frontend health check
echo -n "Frontend (3001): "
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Responding${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

# Log file status
echo -e "\n${BLUE}Log Files:${NC}"
echo "------------------------------"

if [[ -d "logs" ]]; then
    LATEST_LOGS=$(ls -t logs/*.log 2>/dev/null | head -5)
    if [[ -n "$LATEST_LOGS" ]]; then
        echo "$LATEST_LOGS" | while read -r logfile; do
            SIZE=$(wc -l < "$logfile" 2>/dev/null || echo 0)
            echo "  $(basename "$logfile"): $SIZE lines"
        done
    else
        echo -e "${YELLOW}No log files found${NC}"
    fi
else
    echo -e "${YELLOW}No logs directory${NC}"
fi

# Recent activity from logs
echo -e "\n${BLUE}Recent Activity (last 10 entries):${NC}"
echo "------------------------------"

# Find the most recent backend log
LATEST_BACKEND=$(ls -t logs/backend_*.log 2>/dev/null | head -1)
if [[ -f "$LATEST_BACKEND" ]]; then
    echo -e "${CYAN}Backend Log:${NC}"
    tail -10 "$LATEST_BACKEND" 2>/dev/null | grep -E "Processing|Generated|ERROR|WARN|Started" | while IFS= read -r line; do
        if echo "$line" | grep -q "ERROR"; then
            echo -e "  ${RED}[ERROR]${NC} ${line:0:80}..."
        elif echo "$line" | grep -q "WARN"; then
            echo -e "  ${YELLOW}[WARN]${NC} ${line:0:80}..."
        elif echo "$line" | grep -q "Processing user message"; then
            echo -e "  ${GREEN}[CHAT]${NC} ${line:0:80}..."
        else
            echo "  ${line:0:90}..."
        fi
    done
fi

# Performance metrics
echo -e "\n${BLUE}Performance Metrics:${NC}"
echo "------------------------------"

# Memory usage
if [[ -n "$BACKEND_PROCS" ]]; then
    BACKEND_PID=$(echo "$BACKEND_PROCS" | head -1 | awk '{print $2}')
    if [[ -n "$BACKEND_PID" ]]; then
        MEM_USAGE=$(ps -p "$BACKEND_PID" -o %mem= 2>/dev/null || echo "N/A")
        CPU_USAGE=$(ps -p "$BACKEND_PID" -o %cpu= 2>/dev/null || echo "N/A")
        echo "Backend Process:"
        echo "  Memory: ${MEM_USAGE}%"
        echo "  CPU: ${CPU_USAGE}%"
    fi
fi

# Quick actions
echo -e "\n${BLUE}Quick Actions:${NC}"
echo "------------------------------"
echo "1. View live logs:      ./view-logs.sh"
echo "2. Run with logging:    ./run-with-logs.sh"
echo "3. Check status:        ./system-status.sh"
echo "4. Live dashboard:      ./log-dashboard.sh"
echo "5. Test chat:           curl -X POST http://localhost:8080/api/v1/chat -H 'Content-Type: application/json' -d '{\"message\":\"Hello\"}'"

echo -e "\n=============================================="