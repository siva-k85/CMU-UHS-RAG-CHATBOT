#!/bin/bash

# Start Backend with OpenAI API Key
echo "🚀 Starting CMU Health Services Backend with OpenAI API"
echo "=================================================="

# Set the OpenAI API key from environment or prompt user
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Please set OPENAI_API_KEY environment variable"
    echo "Example: export OPENAI_API_KEY='your-api-key'"
    exit 1
fi
export LLM_PROVIDER=openai

echo "✅ OpenAI API Key configured"
echo "✅ LLM Provider set to: openai"

# Use Java 17
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home

echo "Starting backend service..."
./gradlew bootRun