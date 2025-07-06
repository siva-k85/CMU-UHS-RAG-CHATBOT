#!/bin/bash

# Real-time Log Viewer for CMU Health Services Chatbot
echo "📊 CMU Health Services Chatbot - Log Viewer"
echo "=========================================="

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

if [[ -z "$LATEST_BACKEND" && -z "$LATEST_FRONTEND" ]]; then
    echo -e "${RED}No log files found. Run ./run-with-logs.sh first.${NC}"
    exit 1
fi

echo "Monitoring latest logs:"
echo "  Backend:  $LATEST_BACKEND"
echo "  Frontend: $LATEST_FRONTEND"
echo "  System:   $LATEST_SYSTEM"
echo ""

# Function to display logs with color coding
show_logs() {
    echo -e "${BLUE}=== Real-time Log Stream ===${NC}"
    echo "(Press Ctrl+C to exit)"
    echo ""
    
    # Use tail to follow multiple files
    tail -f $LATEST_BACKEND $LATEST_FRONTEND $LATEST_SYSTEM 2>/dev/null | while IFS= read -r line; do
        # Color code based on content
        if echo "$line" | grep -q "ERROR\|Exception\|Failed"; then
            echo -e "${RED}[ERROR]${NC} $line"
        elif echo "$line" | grep -q "WARN\|Warning"; then
            echo -e "${YELLOW}[WARN]${NC} $line"
        elif echo "$line" | grep -q "Processing user message\|chat request\|Chat request"; then
            echo -e "${GREEN}[CHAT]${NC} $line"
        elif echo "$line" | grep -q "INFO\|Started\|Running"; then
            echo -e "${CYAN}[INFO]${NC} $line"
        elif echo "$line" | grep -q "==> "; then
            # File separator from tail
            echo -e "${BLUE}$line${NC}"
        else
            echo "$line"
        fi
    done
}

# Show menu
echo "Select viewing option:"
echo "1) View all logs (combined)"
echo "2) View backend logs only"
echo "3) View frontend logs only"
echo "4) View system logs only"
echo "5) Search logs for errors"
echo "6) Show log statistics"
echo ""
read -p "Enter choice (1-6): " choice

case $choice in
    1)
        show_logs
        ;;
    2)
        echo -e "${BLUE}=== Backend Logs ===${NC}"
        tail -f "$LATEST_BACKEND" 2>/dev/null
        ;;
    3)
        echo -e "${BLUE}=== Frontend Logs ===${NC}"
        tail -f "$LATEST_FRONTEND" 2>/dev/null
        ;;
    4)
        echo -e "${BLUE}=== System Logs ===${NC}"
        tail -f "$LATEST_SYSTEM" 2>/dev/null
        ;;
    5)
        echo -e "${RED}=== Errors in Logs ===${NC}"
        grep -i "error\|exception\|failed" logs/*.log | tail -50
        ;;
    6)
        echo -e "${CYAN}=== Log Statistics ===${NC}"
        echo "Backend log size: $(wc -l < "$LATEST_BACKEND" 2>/dev/null || echo 0) lines"
        echo "Frontend log size: $(wc -l < "$LATEST_FRONTEND" 2>/dev/null || echo 0) lines"
        echo "Chat requests: $(grep -c "chat request" "$LATEST_BACKEND" 2>/dev/null || echo 0)"
        echo "Errors: $(grep -ci "error" logs/*.log 2>/dev/null | awk '{sum += $1} END {print sum}')"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac