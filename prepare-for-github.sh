#!/bin/bash

# Script to prepare the CMU UHS RAG Chatbot repository for GitHub

echo "🚀 Preparing CMU UHS RAG Chatbot for GitHub..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists and remind to not commit it
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  Found .env file - make sure it's in .gitignore${NC}"
fi

# Create .env from example if it doesn't exist
if [ ! -f .env ] && [ -f .env.example ]; then
    echo -e "${GREEN}✅ Creating .env from .env.example${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please update .env with your actual values${NC}"
fi

# Clean build artifacts
echo -e "${GREEN}🧹 Cleaning build artifacts...${NC}"
rm -rf target/
rm -rf build/
rm -rf frontend/node_modules/
rm -rf frontend/.next/
rm -rf frontend/out/
rm -rf scraper/venv/
rm -rf scraper/__pycache__/
find . -name "*.log" -type f -delete
find . -name ".DS_Store" -type f -delete

# Check for sensitive files
echo -e "${GREEN}🔍 Checking for sensitive files...${NC}"
sensitive_files=(".env" "*.key" "*.pem" "*.p12" "*.pfx" "*.crt" "*.csr")
found_sensitive=false

for pattern in "${sensitive_files[@]}"; do
    if find . -name "$pattern" -not -path "./.git/*" -type f | grep -q .; then
        echo -e "${RED}❌ Found sensitive files matching pattern: $pattern${NC}"
        find . -name "$pattern" -not -path "./.git/*" -type f
        found_sensitive=true
    fi
done

if [ "$found_sensitive" = true ]; then
    echo -e "${YELLOW}⚠️  Please ensure all sensitive files are in .gitignore${NC}"
fi

# Verify required files exist
echo -e "${GREEN}📋 Verifying required files...${NC}"
required_files=("README.md" ".gitignore" "LICENSE" "CONTRIBUTING.md" ".env.example")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        echo -e "${RED}❌ $file is missing${NC}"
    fi
done

# Initialize git if not already initialized
if [ ! -d .git ]; then
    echo -e "${GREEN}📂 Initializing git repository...${NC}"
    git init
    git add .
    git commit -m "Initial commit"
fi

# Summary
echo -e "\n${GREEN}📊 Summary:${NC}"
echo "1. Repository cleaned of build artifacts"
echo "2. Sensitive files check completed"
echo "3. Required documentation files verified"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Review and update .env.example with necessary variables"
echo "2. Ensure all API keys and secrets are removed from tracked files"
echo "3. Update README.md with your GitHub repository URL"
echo "4. Add remote origin: git remote add origin <your-repo-url>"
echo "5. Push to GitHub: git push -u origin main"
echo ""
echo -e "${GREEN}✨ Repository is ready for GitHub!${NC}"