#!/bin/bash

# Enhanced CMU Health Services Chatbot Startup Script
# This script starts both backend and frontend services

echo "🚀 Starting Enhanced CMU Health Services Chatbot"
echo "=============================================="

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is already running
if lsof -i :8080 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend is already running on port 8080${NC}"
else
    echo -e "${BLUE}Starting backend...${NC}"
    # Start backend in background
    mvn spring-boot:run > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend starting with PID: $BACKEND_PID"
    echo "Backend logs: tail -f backend.log"
fi

# Check if frontend is already running
if lsof -i :3001 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Frontend is already running on port 3001${NC}"
else
    echo -e "${BLUE}Starting frontend...${NC}"
    # Start frontend in background
    cd frontend && npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend starting with PID: $FRONTEND_PID"
    echo "Frontend logs: tail -f frontend.log"
fi

# Wait for services to start
echo -e "\n${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Check service status
echo -e "\n${GREEN}Service Status:${NC}"
echo "=============================================="

# Check backend
if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend is running at http://localhost:8080"
else
    echo -e "${YELLOW}⚠️${NC} Backend is still starting... Check backend.log"
fi

# Check frontend
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend is running at http://localhost:3001"
else
    echo -e "${YELLOW}⚠️${NC} Frontend is still starting... Check frontend.log"
fi

echo -e "\n${GREEN}🎉 Enhanced Chatbot is ready!${NC}"
echo "=============================================="
echo "Frontend: http://localhost:3001"
echo "Backend API: http://localhost:8080"
echo "Analytics: http://localhost:3001/analytics"
echo ""
echo "To stop services:"
echo "  Backend: kill $BACKEND_PID"
echo "  Frontend: kill $FRONTEND_PID"
echo ""
echo "Logs:"
echo "  Backend: tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo -e "${BLUE}Pro tip:${NC} Try voice input by clicking the microphone icon! 🎤"