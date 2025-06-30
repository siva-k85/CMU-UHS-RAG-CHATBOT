#!/bin/bash

echo "🚀 Starting CMU Health Services RAG Chatbot Full Stack"
echo "=================================================="

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY is not set. The chatbot will run in demo mode."
    echo "Set it with: export OPENAI_API_KEY='your-api-key'"
fi

# Function to cleanup on exit
cleanup() {
    echo "\n🛑 Shutting down..."
    pkill -f "gradlew"
    pkill -f "npm run dev"
    exit 0
}

# Set up trap for cleanup
trap cleanup INT TERM

# Start backend
echo "\n📦 Starting Spring Boot backend..."
cd "$(dirname "$0")"
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
export PATH=$JAVA_HOME/bin:$PATH
./gradlew bootRun &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
while ! curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; do
    sleep 2
done
echo "✅ Backend is running at http://localhost:8080"

# Start frontend
echo "\n🎨 Starting Next.js frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
while ! curl -s http://localhost:3000 > /dev/null 2>&1; do
    sleep 2
done
echo "✅ Frontend is running at http://localhost:3000"

echo "\n🎉 Full stack is running!"
echo "📍 Open http://localhost:3000 in your browser"
echo "Press Ctrl+C to stop both servers"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID