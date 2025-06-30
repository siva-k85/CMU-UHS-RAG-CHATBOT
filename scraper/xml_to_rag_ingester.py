#!/usr/bin/env python3
"""
Ingest XML scraped data into the RAG system
Converts XML files to format suitable for vector embedding
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import List, Dict
import logging
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XMLToRAGIngester:
    def __init__(self, xml_dir: str = "scraped_data_xml", api_url: str = "http://localhost:8080"):
        self.xml_dir = xml_dir
        self.api_url = api_url
        self.documents = []
        
    def parse_xml_file(self, filepath: str) -> Dict:
        """Parse a single XML file and extract content"""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            doc = {
                'url': root.findtext('url', ''),
                'type': root.findtext('type', ''),
                'title': root.findtext('title', ''),
                'is_insurance': root.findtext('is_insurance', 'false').lower() == 'true',
                'scraped_at': root.findtext('scraped_at', ''),
                'content': '',
                'metadata': {}
            }
            
            # Extract content based on type
            if doc['type'] == 'html':
                doc['content'] = self.extract_html_content(root)
                doc['metadata']['description'] = root.findtext('description', '')
                
            elif doc['type'] == 'pdf':
                doc['content'] = self.extract_pdf_content(root)
                # Extract PDF metadata
                pdf_metadata = root.find('pdf_metadata')
                if pdf_metadata:
                    for child in pdf_metadata:
                        doc['metadata'][f'pdf_{child.tag}'] = child.text
            
            return doc
            
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
            return None
    
    def extract_html_content(self, root: ET.Element) -> str:
        """Extract content from HTML page XML"""
        content_parts = []
        
        # Get main content
        content_elem = root.find('content')
        if content_elem:
            # Headings
            headings = content_elem.find('headings')
            if headings:
                for heading in headings.findall('heading'):
                    level = heading.get('level', 'h1')
                    text = heading.text
                    if text:
                        content_parts.append(f"[{level.upper()}] {text}")
            
            # Paragraphs
            paragraphs = content_elem.find('paragraphs')
            if paragraphs:
                for para in paragraphs.findall('paragraph'):
                    if para.text:
                        content_parts.append(para.text)
            
            # Lists
            lists = content_elem.find('lists')
            if lists:
                for lst in lists.findall('list'):
                    list_type = lst.get('type', 'ul')
                    items = []
                    for item in lst.findall('item'):
                        if item.text:
                            items.append(f"• {item.text}")
                    if items:
                        content_parts.append('\n'.join(items))
            
            # Tables
            tables = content_elem.find('tables')
            if tables:
                for table in tables.findall('table'):
                    table_text = "\n[TABLE]\n"
                    for row in table.findall('row'):
                        cells = [cell.text or '' for cell in row.findall('cell')]
                        table_text += ' | '.join(cells) + '\n'
                    content_parts.append(table_text)
            
            # Contact info
            contact = content_elem.find('contact_info')
            if contact:
                contact_parts = []
                for phone in contact.findall('phone'):
                    if phone.text:
                        contact_parts.append(f"Phone: {phone.text}")
                for email in contact.findall('email'):
                    if email.text:
                        contact_parts.append(f"Email: {email.text}")
                if contact_parts:
                    content_parts.append('\n[CONTACT INFO]\n' + '\n'.join(contact_parts))
        
        return '\n\n'.join(content_parts)
    
    def extract_pdf_content(self, root: ET.Element) -> str:
        """Extract content from PDF XML"""
        # Try to get full text first
        full_text = root.findtext('full_text', '')
        if full_text:
            return full_text
        
        # Otherwise, extract from pages
        content_parts = []
        pages = root.find('pages')
        if pages:
            for page in pages.findall('page'):
                page_num = page.get('number', '?')
                page_text = page.text
                if page_text:
                    content_parts.append(f"[PAGE {page_num}]\n{page_text}")
        
        # Add extracted tables
        tables = root.find('extracted_tables')
        if tables:
            for table in tables.findall('table'):
                page_num = table.get('page', '?')
                table_text = f"\n[TABLE on page {page_num}]\n"
                for row in table.findall('row'):
                    cells = [cell.text or '' for cell in row.findall('cell')]
                    table_text += ' | '.join(cells) + '\n'
                content_parts.append(table_text)
        
        return '\n\n'.join(content_parts)
    
    def process_all_xml_files(self):
        """Process all XML files in the directory"""
        logger.info(f"Processing XML files from {self.xml_dir}")
        
        # Process all subdirectories
        for subdir in ['pages', 'insurance', 'pdfs']:
            subdir_path = os.path.join(self.xml_dir, subdir)
            if not os.path.exists(subdir_path):
                continue
                
            for filename in os.listdir(subdir_path):
                if filename.endswith('.xml'):
                    filepath = os.path.join(subdir_path, filename)
                    doc = self.parse_xml_file(filepath)
                    
                    if doc and doc['content']:
                        # Create document for RAG system
                        rag_doc = {
                            'content': doc['content'],
                            'metadata': {
                                'source': 'CMU Health Services',
                                'url': doc['url'],
                                'title': doc['title'],
                                'type': doc['type'],
                                'is_insurance': doc['is_insurance'],
                                'scraped_at': doc['scraped_at'],
                                **doc['metadata']
                            }
                        }
                        self.documents.append(rag_doc)
        
        logger.info(f"Processed {len(self.documents)} documents")
    
    def save_for_ingestion(self, output_file: str = "scraped_data_for_rag.json"):
        """Save documents in format ready for RAG ingestion"""
        output_path = os.path.join(self.xml_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'documents': self.documents,
                'metadata': {
                    'source': 'CMU Health Services Web Scraper',
                    'processed_at': datetime.now().isoformat(),
                    'total_documents': len(self.documents),
                    'insurance_documents': sum(1 for d in self.documents if d['metadata'].get('is_insurance'))
                }
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(self.documents)} documents to {output_path}")
        
        # Generate summary
        insurance_docs = [d for d in self.documents if d['metadata'].get('is_insurance')]
        pdf_docs = [d for d in self.documents if d['metadata'].get('type') == 'pdf']
        
        logger.info(f"Summary:")
        logger.info(f"  - Total documents: {len(self.documents)}")
        logger.info(f"  - Insurance-related: {len(insurance_docs)}")
        logger.info(f"  - PDF documents: {len(pdf_docs)}")
    
    def ingest_to_api(self):
        """Send documents to the RAG API for ingestion"""
        logger.info("Ingesting documents to RAG API...")
        
        endpoint = f"{self.api_url}/api/v1/documents/batch"
        
        # Process in batches
        batch_size = 10
        for i in range(0, len(self.documents), batch_size):
            batch = self.documents[i:i+batch_size]
            
            try:
                response = requests.post(
                    endpoint,
                    json={'documents': batch},
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully ingested batch {i//batch_size + 1}")
                else:
                    logger.error(f"Failed to ingest batch: {response.status_code} - {response.text}")
                    
            except Exception as e:
                logger.error(f"Error ingesting batch: {e}")
        
        logger.info("Ingestion complete!")

def main():
    ingester = XMLToRAGIngester()
    
    # Process XML files
    ingester.process_all_xml_files()
    
    # Save for manual ingestion
    ingester.save_for_ingestion()
    
    # Optionally ingest to API
    try:
        response = requests.get("http://localhost:8080/api/v1/health")
        if response.status_code == 200:
            logger.info("API is available, attempting automatic ingestion...")
            ingester.ingest_to_api()
    except:
        logger.info("API not available. Documents saved for manual ingestion.")

if __name__ == "__main__":
    main()