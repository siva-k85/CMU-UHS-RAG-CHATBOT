#!/usr/bin/env python3
"""
Process the scraped data and create RAG-ready file
"""

import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_scraped_data():
    json_dir = "comprehensive_health_data/json"
    output_file = "comprehensive_health_data/health_services_for_rag.json"
    
    if not os.path.exists(json_dir):
        logger.error(f"Directory {json_dir} not found")
        return
    
    documents = []
    
    # Process each JSON file
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(json_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    page_data = json.load(f)
                
                # Create comprehensive content
                content_parts = [
                    f"Title: {page_data.get('title', 'No Title')}",
                    f"URL: {page_data.get('url', '')}",
                    f"Description: {page_data.get('description', '')}",
                    "",
                    "Main Content:",
                    page_data.get('main_content', page_data.get('full_text', '')),
                    ""
                ]
                
                # Add services
                if page_data.get('services'):
                    content_parts.append("Services Offered:")
                    content_parts.extend(f"- {service}" for service in page_data['services'])
                    content_parts.append("")
                
                # Add hours
                if page_data.get('hours', {}).get('extracted'):
                    content_parts.append("Hours of Operation:")
                    content_parts.extend(page_data['hours']['extracted'])
                    content_parts.append("")
                
                # Add contact info
                contact = page_data.get('contact_info', {})
                if contact.get('phones') or contact.get('emails'):
                    content_parts.append("Contact Information:")
                    if contact.get('phones'):
                        content_parts.extend(f"Phone: {phone}" for phone in contact['phones'])
                    if contact.get('emails'):
                        content_parts.extend(f"Email: {email}" for email in contact['emails'])
                    content_parts.append("")
                
                # Create document
                doc = {
                    'content': '\n'.join(content_parts),
                    'metadata': {
                        'source': 'CMU Health Services Website',
                        'url': page_data.get('url', ''),
                        'title': page_data.get('title', ''),
                        'type': 'webpage',
                        'scraped_at': page_data.get('scraped_at', datetime.now().isoformat())
                    }
                }
                
                documents.append(doc)
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
    
    # Save RAG-ready file
    output_data = {
        'documents': documents,
        'metadata': {
            'source': 'CMU Health Services Comprehensive Scrape',
            'scrape_date': datetime.now().isoformat(),
            'total_documents': len(documents)
        }
    }
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Processed {len(documents)} documents")
    logger.info(f"Saved to {output_file}")

if __name__ == "__main__":
    process_scraped_data()