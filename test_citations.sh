#!/bin/bash

echo "🧪 Testing CMU Health Services RAG Chatbot with Citations"
echo "========================================================"
echo ""

# Test questions
questions=(
    "What are the health center hours?"
    "How do I schedule an appointment at CMU health services?"
    "What insurance does CMU accept?"
    "Where is the health center located on campus?"
    "What mental health services are available for students?"
)

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API endpoint
API_URL="http://localhost:8080/api/v2/chat"

# Loop through questions
for question in "${questions[@]}"; do
    echo -e "${YELLOW}❓ Question:${NC} $question"
    echo ""
    
    # Make API call
    response=$(curl -s -X POST $API_URL \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$question\"}")
    
    # Extract response and citations using jq
    if command -v jq &> /dev/null; then
        answer=$(echo $response | jq -r '.response // .message // "No response"')
        citations=$(echo $response | jq -r '.citations // []')
        
        echo -e "${GREEN}💬 Answer:${NC}"
        echo "$answer" | fold -w 80 -s
        echo ""
        
        # Check if there are citations
        if [ "$citations" != "[]" ]; then
            echo -e "${BLUE}📚 Sources:${NC}"
            echo $response | jq -r '.citations[] | "   • \(.title)\n     URL: \(.url)\n     \(.snippet)"'
        fi
    else
        # Fallback without jq
        echo "$response"
    fi
    
    echo ""
    echo "---"
    echo ""
    
    # Small delay between requests
    sleep 1
done

echo "✅ Testing complete!"