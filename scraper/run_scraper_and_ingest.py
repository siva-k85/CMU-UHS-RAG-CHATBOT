#!/usr/bin/env python3
"""
Script to scrape CMU Health Services and ingest into RAG system
"""

import os
import sys
import subprocess
import requests
import json
import time
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    requirements = [
        'requests',
        'beautifulsoup4',
        'lxml'
    ]
    
    print("Installing required packages...")
    for package in requirements:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def run_scraper():
    """Run the CMU health scraper"""
    print("\n🕷️ Starting CMU Health Services web scraper...")
    
    # Import and run scraper
    from cmu_health_scraper import CMUHealthScraper
    
    scraper = CMUHealthScraper(
        base_url="https://www.cmu.edu/health-services/",
        delay=1.5,  # Respectful delay
        max_depth=3  # Reasonable depth
    )
    
    summary = scraper.run()
    
    print(f"\n✅ Scraping completed!")
    print(f"   - Total pages scraped: {summary['total_pages']}")
    print(f"   - Time taken: {summary['scrape_time']:.2f} seconds")
    print(f"   - Categories found: {json.dumps(summary['categories'], indent=2)}")
    
    return summary

def ingest_to_rag(scraped_data_path: str = "scraped_data"):
    """Ingest scraped data into the RAG system"""
    print("\n📤 Ingesting scraped data into RAG system...")
    
    # Check if backend is running
    try:
        health_check = requests.get("http://localhost:8080/api/v1/health")
        if health_check.status_code != 200:
            print("❌ Backend is not running. Please start the Spring Boot application first.")
            return False
    except:
        print("❌ Cannot connect to backend. Please ensure it's running on http://localhost:8080")
        return False
    
    # Prepare ingestion request
    ingest_url = "http://localhost:8080/api/v2/ingest/scraped-data"
    
    try:
        response = requests.post(
            ingest_url,
            json={"path": scraped_data_path},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Ingestion completed!")
            print(f"   - Total documents: {result.get('total_documents', 0)}")
            print(f"   - Successfully ingested: {result.get('successfully_ingested', 0)}")
            
            if result.get('errors'):
                print(f"   - Errors: {len(result['errors'])}")
                for error in result['errors'][:5]:  # Show first 5 errors
                    print(f"     • {error}")
            
            return True
        else:
            print(f"❌ Ingestion failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during ingestion: {str(e)}")
        return False

def test_chatbot_with_citations():
    """Test the chatbot with a sample query"""
    print("\n🧪 Testing chatbot with citations...")
    
    test_questions = [
        "What are the health center hours?",
        "How do I schedule an appointment?",
        "What insurance does CMU health services accept?",
        "Where is the health center located?",
        "What mental health services are available?"
    ]
    
    chat_url = "http://localhost:8080/api/v2/chat"
    
    for question in test_questions[:2]:  # Test first 2 questions
        print(f"\n❓ Question: {question}")
        
        try:
            response = requests.post(
                chat_url,
                json={"message": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"💬 Response: {result.get('response', 'No response')[:200]}...")
                
                citations = result.get('citations', [])
                if citations:
                    print(f"\n📚 Citations ({len(citations)}):")
                    for i, citation in enumerate(citations, 1):
                        print(f"   [{i}] {citation.get('title', 'Unknown')}")
                        print(f"       URL: {citation.get('url', 'No URL')}")
                        print(f"       Snippet: {citation.get('snippet', '')[:100]}...")
            else:
                print(f"❌ Failed to get response: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing chatbot: {str(e)}")
        
        time.sleep(1)  # Small delay between questions

def main():
    """Main execution function"""
    print("🏥 CMU Health Services RAG System - Web Scraper & Ingestion")
    print("=" * 60)
    
    # Step 1: Install requirements
    install_requirements()
    
    # Step 2: Run scraper
    summary = run_scraper()
    
    if summary['total_pages'] == 0:
        print("❌ No pages were scraped. Please check the scraper configuration.")
        return
    
    # Step 3: Ingest into RAG
    if ingest_to_rag():
        # Step 4: Test the system
        test_chatbot_with_citations()
        
        print("\n✅ All done! The CMU Health Services RAG system is now updated with fresh data.")
        print("   You can test it at: http://localhost:3000")
    else:
        print("\n⚠️  Scraping completed but ingestion failed. Please check the backend logs.")

if __name__ == "__main__":
    main()