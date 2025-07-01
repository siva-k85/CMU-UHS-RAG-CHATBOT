#!/bin/bash

echo "🚀 Starting CMU UHS RAG Chatbot (Full Featured Version)"
echo "======================================================="
echo ""

# Set Java 17
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home

# Enable all services (with fallbacks)
export SPRING_PROFILES_ACTIVE=dev
export OPENAI_API_KEY=${OPENAI_API_KEY:-demo}
export ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-demo}

echo "✅ Configuration:"
echo "   - Java: $($JAVA_HOME/bin/java -version 2>&1 | head -1)"
echo "   - Profile: dev (security disabled)"
echo "   - LLM: Demo mode"
echo ""

echo "📦 Building application..."
./gradlew clean build -x test --no-daemon

echo ""
echo "🏃 Starting application..."
echo "Access at: http://localhost:8080"
echo ""

# Run in foreground
./gradlew bootRun --no-daemon