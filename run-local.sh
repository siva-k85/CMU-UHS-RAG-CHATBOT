#!/bin/bash

echo "Starting CMU UHS RAG Chatbot..."
echo "================================"

# Check Java version
java -version 2>&1 | grep -q "version \"17" || echo "WARNING: Java 17 is recommended"

# Set environment variables
export OPENAI_API_KEY=${OPENAI_API_KEY:-}
export ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
export LLM_PROVIDER=${LLM_PROVIDER:-openai}
export REDIS_HOST=${REDIS_HOST:-localhost}
export REDIS_PORT=${REDIS_PORT:-6379}
export CHROMA_URL=${CHROMA_URL:-http://localhost:8000}

# Display configuration
echo "Configuration:"
echo "- LLM Provider: $LLM_PROVIDER"
echo "- Redis: $REDIS_HOST:$REDIS_PORT"
echo "- Chroma: $CHROMA_URL"

if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "WARNING: No API keys set. Running in demo mode."
fi

echo ""

# Build and run
echo "Building application..."
./gradlew clean build -x test || exit 1

echo "Starting application..."
./gradlew bootRun