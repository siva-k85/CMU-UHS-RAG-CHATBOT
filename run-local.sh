#!/bin/bash

echo "Starting CMU UHS RAG Chatbot locally..."

# Set environment variables
export OPENAI_API_KEY=${OPENAI_API_KEY:-demo}
export ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-demo}
export LLM_PROVIDER=${LLM_PROVIDER:-openai}

# Optional services (will use fallbacks if not available)
export REDIS_HOST=${REDIS_HOST:-localhost}
export REDIS_PORT=${REDIS_PORT:-6379}
export CHROMA_URL=${CHROMA_URL:-http://localhost:8000}

echo "Configuration:"
echo "- LLM Provider: $LLM_PROVIDER"
echo "- Redis: $REDIS_HOST:$REDIS_PORT"
echo "- Chroma: $CHROMA_URL"
echo ""

# Build the project
echo "Building the application..."
./gradlew clean build -x test

if [ $? -ne 0 ]; then
    echo "Build failed. Trying with bootJar task..."
    ./gradlew bootJar
fi

# Run the application
echo "Starting the application..."
./gradlew bootRun