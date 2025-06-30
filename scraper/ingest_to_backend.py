#!/usr/bin/env python3
"""
Ingest scraped CMU Health data into the Spring Boot RAG backend
"""

import json
import requests
import logging
import time
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGIngester:
    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url
        self.batch_endpoint = f"{api_url}/api/v1/documents/batch"
        self.count_endpoint = f"{api_url}/api/v1/documents/count"
        
    def check_backend_health(self) -> bool:
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def load_scraped_data(self, filepath: str = "scraped_data_xml/scraped_data_for_rag.json") -> List[Dict]:
        """Load the processed scraped data"""
        logger.info(f"Loading data from {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = data.get('documents', [])
        logger.info(f"Loaded {len(documents)} documents")
        
        # Log summary
        insurance_docs = sum(1 for d in documents if d['metadata'].get('is_insurance'))
        pdf_docs = sum(1 for d in documents if d['metadata'].get('type') == 'pdf')
        
        logger.info(f"Document breakdown:")
        logger.info(f"  - Insurance-related: {insurance_docs}")
        logger.info(f"  - PDF documents: {pdf_docs}")
        logger.info(f"  - HTML pages: {len(documents) - pdf_docs}")
        
        return documents
    
    def get_document_count(self) -> int:
        """Get current document count from backend"""
        try:
            response = requests.get(self.count_endpoint)
            if response.status_code == 200:
                return response.json().get('count', -1)
        except:
            pass
        return -1
    
    def ingest_batch(self, documents: List[Dict], batch_size: int = 10) -> Dict[str, int]:
        """Ingest documents in batches"""
        results = {
            'total': len(documents),
            'success': 0,
            'failed': 0,
            'batches': 0
        }
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(f"Processing batch {batch_num} ({len(batch)} documents)")
            
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
                    logger.info(f"Batch {batch_num} completed: {result}")
                else:
                    logger.error(f"Batch {batch_num} failed: {response.status_code} - {response.text}")
                    results['failed'] += len(batch)
                    
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}")
                results['failed'] += len(batch)
            
            # Small delay between batches
            time.sleep(0.5)
        
        return results
    
    def run_ingestion(self):
        """Main ingestion process"""
        logger.info("Starting RAG ingestion process")
        
        # Check backend
        if not self.check_backend_health():
            logger.error("Backend is not available. Please ensure Spring Boot application is running.")
            logger.info("Start the backend with: ./gradlew bootRun")
            return
        
        logger.info("Backend is available")
        
        # Get initial count
        initial_count = self.get_document_count()
        logger.info(f"Initial document count: {initial_count}")
        
        # Load data
        documents = self.load_scraped_data()
        
        if not documents:
            logger.error("No documents to ingest")
            return
        
        # Ingest documents
        logger.info("Starting batch ingestion...")
        results = self.ingest_batch(documents, batch_size=10)
        
        # Get final count
        final_count = self.get_document_count()
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("INGESTION COMPLETE")
        logger.info("="*50)
        logger.info(f"Total documents: {results['total']}")
        logger.info(f"Successfully ingested: {results['success']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Batches processed: {results['batches']}")
        logger.info(f"Final document count: {final_count}")
        logger.info("="*50)
        
        # Save ingestion report
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results,
            'initial_count': initial_count,
            'final_count': final_count
        }
        
        with open('scraped_data_xml/ingestion_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("Ingestion report saved to scraped_data_xml/ingestion_report.json")

def main():
    ingester = RAGIngester()
    ingester.run_ingestion()

if __name__ == "__main__":
    main()