#!/bin/bash

# Run CMU Health Services Chatbot with Log Monitoring
echo "🚀 Starting CMU Health Services Chatbot with Log Monitoring"
echo "=========================================================="

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Create logs directory if it doesn't exist
mkdir -p logs

# Set timestamp for log files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Log files
BACKEND_LOG="logs/backend_${TIMESTAMP}.log"
FRONTEND_LOG="logs/frontend_${TIMESTAMP}.log"
SYSTEM_LOG="logs/system_${TIMESTAMP}.log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$SYSTEM_LOG"
}

# Clean up function
cleanup() {
    log "Shutting down services..."
    pkill -f "gradlew bootRun" || true
    pkill -f "next dev.*3001" || true
    echo -e "\n${YELLOW}Services stopped. Logs saved in:${NC}"
    echo "  Backend: $BACKEND_LOG"
    echo "  Frontend: $FRONTEND_LOG"
    echo "  System: $SYSTEM_LOG"
    exit 0
}

# Set up trap for clean shutdown
trap cleanup INT TERM

# Start backend with logs
log "Starting backend service..."
# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    log "WARNING: OPENAI_API_KEY not set. Running in demo mode."
    log "To enable AI features, set: export OPENAI_API_KEY='your-api-key'"
else
    log "OpenAI API key detected"
fi
export LLM_PROVIDER=${LLM_PROVIDER:-openai}
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home

# Start backend
./gradlew bootRun > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
log "Backend started with PID: $BACKEND_PID"

# Start frontend with logs
log "Starting frontend service..."
cd frontend && npm run dev > "../$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
cd ..
log "Frontend started with PID: $FRONTEND_PID"

# Wait for services to start
echo -e "\n${YELLOW}Waiting for services to initialize...${NC}"
sleep 15

# Check services
echo -e "\n${GREEN}Service Status:${NC}"
if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    log "✓ Backend is running at http://localhost:8080"
else
    log "✗ Backend failed to start - check $BACKEND_LOG"
fi

if curl -s http://localhost:3001 > /dev/null 2>&1; then
    log "✓ Frontend is running at http://localhost:3001"
else
    log "✗ Frontend failed to start - check $FRONTEND_LOG"
fi

# Display monitoring info
echo -e "\n${BLUE}📊 Log Monitoring Active${NC}"
echo "=========================================================="
echo "Logs are being written to:"
echo "  Backend:  $BACKEND_LOG"
echo "  Frontend: $FRONTEND_LOG"
echo "  System:   $SYSTEM_LOG"
echo ""
echo "Monitor logs in real-time:"
echo "  Backend:  tail -f $BACKEND_LOG"
echo "  Frontend: tail -f $FRONTEND_LOG"
echo "  All:      tail -f logs/*.log"
echo ""
echo -e "${GREEN}Access Points:${NC}"
echo "  Main App: http://localhost:3001"
echo "  Analytics: http://localhost:3001/analytics"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo "=========================================================="

# Function to monitor and display important log events
monitor_logs() {
    while true; do
        # Check for errors in backend log
        if tail -n 10 "$BACKEND_LOG" 2>/dev/null | grep -i "error\|exception" > /dev/null; then
            echo -e "\n${RED}⚠️  Backend error detected - check $BACKEND_LOG${NC}"
        fi
        
        # Check for API calls
        if tail -n 10 "$BACKEND_LOG" 2>/dev/null | grep -i "Processing user message\|chat request" > /dev/null; then
            echo -e "${GREEN}📨 Chat request processed${NC}"
        fi
        
        sleep 5
    done
}

# Start monitoring in background
monitor_logs &
MONITOR_PID=$!

# Keep script running
while true; do
    sleep 1
done