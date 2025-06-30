#!/bin/bash

# CMU Health Services RAG Chatbot - Complete System Runner
# This script starts all components and ingests the scraped data

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}===========================================${NC}"
echo -e "${BLUE}CMU Health Services RAG Chatbot${NC}"
echo -e "${BLUE}Complete System Startup${NC}"
echo -e "${BLUE}===========================================${NC}"

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}Waiting for $service_name to start...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null; then
            echo -e "${GREEN}✓ $service_name is ready${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}✗ $service_name failed to start${NC}"
    return 1
}

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY not set${NC}"
    echo "The system will run in demo mode"
    echo "To use OpenAI, set: export OPENAI_API_KEY='your-key'"
    echo ""
fi

# Step 1: Start Backend
echo -e "\n${BLUE}[1/4] Starting Spring Boot Backend...${NC}"

if check_port 8080; then
    echo -e "${YELLOW}Backend already running on port 8080${NC}"
else
    cd "$(dirname "$0")"
    echo "Starting backend in background..."
    ./gradlew bootRun > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    # Wait for backend to be ready
    wait_for_service "http://localhost:8080/api/v1/health" "Backend"
fi

# Step 2: Start Frontend
echo -e "\n${BLUE}[2/4] Starting Next.js Frontend...${NC}"

if check_port 3000; then
    echo -e "${YELLOW}Frontend already running on port 3000${NC}"
else
    cd frontend
    echo "Installing frontend dependencies..."
    npm install
    
    echo "Starting frontend in background..."
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    cd ..
    
    # Wait for frontend to be ready
    wait_for_service "http://localhost:3000" "Frontend"
fi

# Step 3: Ingest Scraped Data
echo -e "\n${BLUE}[3/4] Ingesting Scraped CMU Health Data...${NC}"

cd scraper

# Check if scraped data exists
if [ -f "scraped_data_xml/scraped_data_for_rag.json" ]; then
    echo "Found scraped data, starting ingestion..."
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python3 ingest_to_backend.py
else
    echo -e "${YELLOW}No scraped data found. Run the scraper first:${NC}"
    echo "  cd scraper"
    echo "  python3 run_enhanced_scraper.py"
fi

cd ..

# Step 4: Display Status
echo -e "\n${BLUE}[4/4] System Status${NC}"
echo -e "${BLUE}===========================================${NC}"

if curl -s "http://localhost:8080/api/v1/documents/count" > /dev/null; then
    DOC_COUNT=$(curl -s "http://localhost:8080/api/v1/documents/count" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo -e "${GREEN}✓ Backend API: http://localhost:8080${NC}"
    echo -e "${GREEN}  Documents in vector store: $DOC_COUNT${NC}"
else
    echo -e "${RED}✗ Backend API not responding${NC}"
fi

if curl -s "http://localhost:3000" > /dev/null; then
    echo -e "${GREEN}✓ Frontend UI: http://localhost:3000${NC}"
else
    echo -e "${RED}✗ Frontend not responding${NC}"
fi

echo -e "\n${BLUE}===========================================${NC}"
echo -e "${GREEN}System is ready!${NC}"
echo -e "\n${BLUE}Access the chatbot at: http://localhost:3000${NC}"
echo -e "\n${YELLOW}Example queries to try:${NC}"
echo "  - What insurance plans does CMU offer?"
echo "  - What are the health center hours?"
echo "  - How do I file an insurance claim?"
echo "  - What mental health services are available?"
echo "  - Tell me about the student health insurance plan"
echo ""
echo -e "${YELLOW}To stop all services:${NC}"
echo "  Press Ctrl+C or run: pkill -f 'gradle|npm'"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "  Backend: tail -f backend.log"
echo "  Frontend: tail -f frontend.log"

# Keep script running
echo -e "\n${BLUE}Press Ctrl+C to stop all services${NC}"
trap "echo -e '\n${YELLOW}Stopping services...${NC}'; pkill -P $$; exit" INT
wait