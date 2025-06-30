#!/usr/bin/env python3
"""
Ingest comprehensive CMU Health Services data into the RAG system
This script processes the thoroughly scraped data and adds it to the vector store
"""

import json
import requests
import logging
import time
import os
from typing import List, Dict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveDataIngester:
    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url
        self.batch_endpoint = f"{api_url}/api/v1/documents/batch"
        self.count_endpoint = f"{api_url}/api/v1/documents/count"
        self.clear_endpoint = f"{api_url}/api/v1/documents/clear"
        
    def check_backend_health(self) -> bool:
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_current_count(self) -> int:
        """Get current document count"""
        try:
            response = requests.get(self.count_endpoint)
            if response.status_code == 200:
                return response.json().get('count', 0)
        except:
            pass
        return 0
    
    def clear_existing_documents(self) -> bool:
        """Clear existing documents to ensure fresh data"""
        try:
            response = requests.delete(self.clear_endpoint)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to clear documents: {e}")
            return False
    
    def load_comprehensive_data(self) -> List[Dict]:
        """Load the comprehensively scraped data"""
        # Check multiple possible locations
        data_paths = [
            "comprehensive_health_data/health_services_for_rag.json",
            "health_services_for_rag.json",
            "../comprehensive_health_data/health_services_for_rag.json"
        ]
        
        for path in data_paths:
            if os.path.exists(path):
                logger.info(f"Loading data from {path}")
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('documents', [])
        
        logger.error("Could not find comprehensive data file")
        return []
    
    def load_previous_data(self) -> List[Dict]:
        """Load previously scraped data to merge"""
        previous_path = "scraped_data_xml/scraped_data_for_rag.json"
        if os.path.exists(previous_path):
            logger.info(f"Loading previous data from {previous_path}")
            with open(previous_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('documents', [])
        return []
    
    def merge_documents(self, comprehensive: List[Dict], previous: List[Dict]) -> List[Dict]:
        """Merge comprehensive and previous data, removing duplicates"""
        # Create a set of URLs from comprehensive data
        comprehensive_urls = {doc['metadata'].get('url', '') for doc in comprehensive}
        
        # Add previous documents that aren't in comprehensive
        merged = comprehensive.copy()
        added_from_previous = 0
        
        for doc in previous:
            doc_url = doc['metadata'].get('url', '')
            if doc_url and doc_url not in comprehensive_urls:
                merged.append(doc)
                added_from_previous += 1
        
        logger.info(f"Merged documents: {len(comprehensive)} comprehensive + {added_from_previous} unique from previous = {len(merged)} total")
        return merged
    
    def enhance_documents(self, documents: List[Dict]) -> List[Dict]:
        """Enhance documents with additional metadata"""
        enhanced = []
        
        for doc in documents:
            # Ensure all documents have proper metadata
            if 'metadata' not in doc:
                doc['metadata'] = {}
            
            # Add ingestion timestamp
            doc['metadata']['ingested_at'] = datetime.now().isoformat()
            
            # Categorize documents
            content_lower = doc.get('content', '').lower()
            metadata = doc.get('metadata', {})
            
            # Determine categories
            categories = []
            if any(word in content_lower for word in ['insurance', 'billing', 'payment', 'cost', 'fee']):
                categories.append('insurance')
            if any(word in content_lower for word in ['appointment', 'schedule', 'visit']):
                categories.append('appointments')
            if any(word in content_lower for word in ['counseling', 'mental', 'psychological', 'therapy']):
                categories.append('mental_health')
            if any(word in content_lower for word in ['pharmacy', 'prescription', 'medication']):
                categories.append('pharmacy')
            if any(word in content_lower for word in ['immunization', 'vaccine', 'vaccination']):
                categories.append('immunizations')
            if any(word in content_lower for word in ['hours', 'open', 'closed']):
                categories.append('hours')
            if any(word in content_lower for word in ['emergency', 'urgent', 'crisis']):
                categories.append('emergency')
            
            metadata['categories'] = categories
            doc['metadata'] = metadata
            
            enhanced.append(doc)
        
        return enhanced
    
    def ingest_documents(self, documents: List[Dict], batch_size: int = 5) -> Dict[str, int]:
        """Ingest documents in small batches"""
        results = {
            'total': len(documents),
            'success': 0,
            'failed': 0,
            'batches': 0
        }
        
        logger.info(f"Starting ingestion of {len(documents)} documents in batches of {batch_size}")
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(f"Processing batch {batch_num}/{(len(documents) + batch_size - 1) // batch_size}")
            
            try:
                response = requests.post(
                    self.batch_endpoint,
                    json={'documents': batch},
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    results['success'] += result.get('success', 0)
                    results['failed'] += result.get('failed', 0)
                    results['batches'] += 1
                    logger.info(f"Batch {batch_num} completed successfully")
                else:
                    logger.error(f"Batch {batch_num} failed: {response.status_code}")
                    results['failed'] += len(batch)
                    
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}")
                results['failed'] += len(batch)
            
            # Small delay between batches
            time.sleep(0.2)
        
        return results
    
    def run_comprehensive_ingestion(self, clear_existing: bool = False):
        """Main ingestion process"""
        logger.info("=" * 60)
        logger.info("Starting Comprehensive CMU Health Services Data Ingestion")
        logger.info("=" * 60)
        
        # Check backend
        if not self.check_backend_health():
            logger.error("Backend is not available. Please ensure Spring Boot application is running.")
            return
        
        logger.info("Backend is available")
        
        # Get initial count
        initial_count = self.get_current_count()
        logger.info(f"Initial document count: {initial_count}")
        
        # Optionally clear existing documents
        if clear_existing:
            logger.info("Clearing existing documents...")
            if self.clear_existing_documents():
                logger.info("Documents cleared successfully")
                initial_count = 0
            else:
                logger.warning("Failed to clear documents, continuing with existing data")
        
        # Load comprehensive data
        comprehensive_docs = self.load_comprehensive_data()
        if not comprehensive_docs:
            logger.error("No comprehensive data found. Please run comprehensive_health_scraper.py first")
            return
        
        logger.info(f"Loaded {len(comprehensive_docs)} comprehensive documents")
        
        # Load and merge with previous data
        if not clear_existing:
            previous_docs = self.load_previous_data()
            if previous_docs:
                all_docs = self.merge_documents(comprehensive_docs, previous_docs)
            else:
                all_docs = comprehensive_docs
        else:
            all_docs = comprehensive_docs
        
        # Enhance documents
        enhanced_docs = self.enhance_documents(all_docs)
        
        # Ingest documents
        logger.info("Starting document ingestion...")
        results = self.ingest_documents(enhanced_docs, batch_size=5)
        
        # Get final count
        time.sleep(2)  # Wait for ingestion to complete
        final_count = self.get_current_count()
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("INGESTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Documents processed: {results['total']}")
        logger.info(f"Successfully ingested: {results['success']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Initial count: {initial_count}")
        logger.info(f"Final count: {final_count}")
        logger.info(f"New documents added: {final_count - initial_count}")
        logger.info("=" * 60)
        
        # Save ingestion report
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'initial_count': initial_count,
            'final_count': final_count,
            'documents_added': final_count - initial_count,
            'comprehensive': True
        }
        
        report_path = 'comprehensive_ingestion_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Ingestion report saved to {report_path}")
        
        # Provide sample queries
        logger.info("\n" + "=" * 60)
        logger.info("SAMPLE QUERIES TO TEST")
        logger.info("=" * 60)
        logger.info("1. What are all the services offered at CMU Health Services?")
        logger.info("2. How do I schedule an appointment?")
        logger.info("3. What insurance plans are accepted?")
        logger.info("4. What are the pharmacy hours?")
        logger.info("5. Tell me about mental health services")
        logger.info("6. What immunizations are required?")
        logger.info("7. Where is the health center located?")
        logger.info("8. What should I do in an emergency?")
        logger.info("=" * 60)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Ingest comprehensive CMU Health Services data')
    parser.add_argument('--clear', action='store_true', help='Clear existing documents before ingesting')
    args = parser.parse_args()
    
    ingester = ComprehensiveDataIngester()
    ingester.run_comprehensive_ingestion(clear_existing=args.clear)

if __name__ == "__main__":
    main()