#!/usr/bin/env python3
"""
Enhanced CMU Health Services Web Scraper
Extracts all content including PDFs and saves in XML format
"""

import os
import sys
import time
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import PyPDF2
import pdfplumber
from datetime import datetime
import hashlib
import re
from typing import Dict, List, Set, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import mimetypes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedCMUHealthScraper:
    def __init__(self, output_dir: str = "scraped_data_xml"):
        self.output_dir = output_dir
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.pdf_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "pdfs"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "pages"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "insurance"), exist_ok=True)
        
        # CMU Health Services domains and paths
        self.allowed_domains = [
            'www.cmu.edu/health-services',
            'www.cmu.edu/counseling',
            'www.cmu.edu/wellness',
            'www.cmu.edu/student-affairs/health',
            'www.cmu.edu/hr/benefits/insurance'
        ]
        
        self.start_urls = [
            'https://www.cmu.edu/health-services/',
            'https://www.cmu.edu/health-services/student-insurance/',
            'https://www.cmu.edu/health-services/student-insurance/index.html',
            'https://www.cmu.edu/health-services/billing-insurance/',
            'https://www.cmu.edu/health-services/pharmacy/',
            'https://www.cmu.edu/health-services/services/',
            'https://www.cmu.edu/counseling/',
            'https://www.cmu.edu/wellness/'
        ]
        
        # Insurance-related keywords
        self.insurance_keywords = [
            'insurance', 'coverage', 'benefits', 'claim', 'copay', 'deductible',
            'premium', 'enrollment', 'aetna', 'policy', 'reimbursement',
            'billing', 'payment', 'cost', 'fee', 'charge', 'waiver'
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """Extract text and metadata from PDF file"""
        logger.info(f"Extracting text from PDF: {pdf_path}")
        
        extracted_data = {
            'text': '',
            'metadata': {},
            'pages': [],
            'tables': []
        }
        
        try:
            # Try with pdfplumber first (better for tables)
            with pdfplumber.open(pdf_path) as pdf:
                extracted_data['metadata'] = {
                    'pages': len(pdf.pages),
                    'author': pdf.metadata.get('Author', ''),
                    'title': pdf.metadata.get('Title', ''),
                    'subject': pdf.metadata.get('Subject', ''),
                    'creation_date': str(pdf.metadata.get('CreationDate', ''))
                }
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ''
                    extracted_data['pages'].append({
                        'page_number': i + 1,
                        'text': page_text
                    })
                    extracted_data['text'] += page_text + '\n\n'
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            extracted_data['tables'].append({
                                'page': i + 1,
                                'data': table
                            })
            
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    extracted_data['metadata'] = {
                        'pages': len(pdf_reader.pages),
                        'info': pdf_reader.metadata if pdf_reader.metadata else {}
                    }
                    
                    for i, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        extracted_data['pages'].append({
                            'page_number': i + 1,
                            'text': page_text
                        })
                        extracted_data['text'] += page_text + '\n\n'
                        
            except Exception as e2:
                logger.error(f"Failed to extract PDF {pdf_path}: {e2}")
                extracted_data['error'] = str(e2)
        
        return extracted_data

    def download_pdf(self, url: str) -> Optional[str]:
        """Download PDF and return local path"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Generate filename from URL
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = os.path.basename(urlparse(url).path) or f"document_{url_hash}.pdf"
            
            # Ensure it has .pdf extension
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # Check if it's insurance-related
            is_insurance = any(keyword in url.lower() or keyword in filename.lower() 
                             for keyword in self.insurance_keywords)
            
            if is_insurance:
                filepath = os.path.join(self.output_dir, "insurance", filename)
            else:
                filepath = os.path.join(self.output_dir, "pdfs", filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded PDF: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download PDF {url}: {e}")
            return None

    def scrape_page(self, url: str) -> Optional[Dict]:
        """Scrape a single page and extract all information"""
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        logger.info(f"Scraping: {url}")
        
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            # Handle PDFs
            if 'application/pdf' in content_type or url.endswith('.pdf'):
                self.pdf_urls.add(url)
                pdf_path = self.download_pdf(url)
                if pdf_path:
                    pdf_data = self.extract_text_from_pdf(pdf_path)
                    return {
                        'url': url,
                        'type': 'pdf',
                        'title': os.path.basename(pdf_path),
                        'content': pdf_data,
                        'scraped_at': datetime.now().isoformat(),
                        'is_insurance': any(kw in url.lower() for kw in self.insurance_keywords)
                    }
                return None
            
            # Handle HTML pages
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract metadata
            title = soup.find('title')
            title_text = title.text.strip() if title else 'No Title'
            
            meta_description = soup.find('meta', {'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''
            
            # Extract main content
            main_content = self.extract_main_content(soup)
            
            # Extract structured data
            structured_data = self.extract_structured_data(soup)
            
            # Find all links
            links = []
            for link in soup.find_all(['a', 'link']):
                href = link.get('href')
                if href:
                    absolute_url = urljoin(url, href)
                    link_text = link.text.strip() if link.text else ''
                    links.append({
                        'url': absolute_url,
                        'text': link_text,
                        'is_pdf': absolute_url.endswith('.pdf') or 'pdf' in link_text.lower()
                    })
            
            # Check if page is insurance-related
            page_text = soup.get_text().lower()
            is_insurance = any(keyword in page_text for keyword in self.insurance_keywords)
            
            return {
                'url': url,
                'type': 'html',
                'title': title_text,
                'description': description,
                'content': main_content,
                'structured_data': structured_data,
                'links': links,
                'scraped_at': datetime.now().isoformat(),
                'is_insurance': is_insurance
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            self.failed_urls.add(url)
            return None

    def extract_main_content(self, soup: BeautifulSoup) -> Dict:
        """Extract main content from page"""
        content = {
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'tables': [],
            'contact_info': {},
            'hours': {},
            'services': []
        }
        
        # Extract headings
        for tag in ['h1', 'h2', 'h3', 'h4']:
            for heading in soup.find_all(tag):
                content['headings'].append({
                    'level': tag,
                    'text': heading.text.strip()
                })
        
        # Extract paragraphs
        for p in soup.find_all('p'):
            text = p.text.strip()
            if text:
                content['paragraphs'].append(text)
        
        # Extract lists
        for list_tag in soup.find_all(['ul', 'ol']):
            items = [li.text.strip() for li in list_tag.find_all('li') if li.text.strip()]
            if items:
                content['lists'].append({
                    'type': list_tag.name,
                    'items': items
                })
        
        # Extract tables
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
                if cells:
                    table_data.append(cells)
            if table_data:
                content['tables'].append(table_data)
        
        # Extract contact information
        phone_pattern = re.compile(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})')
        email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        
        text = soup.get_text()
        phones = phone_pattern.findall(text)
        emails = email_pattern.findall(text)
        
        if phones:
            content['contact_info']['phones'] = list(set(phones))
        if emails:
            content['contact_info']['emails'] = list(set(emails))
        
        # Extract hours
        hours_patterns = [
            r'(?:Monday|Mon).*?(?:AM|PM|am|pm)',
            r'(?:Hours|Open).*?(?:AM|PM|am|pm)'
        ]
        for pattern in hours_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                content['hours']['extracted'] = matches
        
        return content

    def extract_structured_data(self, soup: BeautifulSoup) -> Dict:
        """Extract structured data like JSON-LD, microdata, etc."""
        structured = {}
        
        # Look for JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            structured['json_ld'] = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    structured['json_ld'].append(data)
                except:
                    pass
        
        # Look for specific CMU health divs/classes
        health_divs = soup.find_all('div', class_=re.compile('health|medical|insurance'))
        if health_divs:
            structured['health_sections'] = []
            for div in health_divs[:5]:  # Limit to prevent too much data
                structured['health_sections'].append({
                    'class': div.get('class', []),
                    'id': div.get('id', ''),
                    'text': div.text.strip()[:500]  # First 500 chars
                })
        
        return structured

    def save_to_xml(self, data: Dict, filename: str):
        """Save scraped data to XML format"""
        root = ET.Element('webpage')
        
        # Add basic metadata
        ET.SubElement(root, 'url').text = data.get('url', '')
        ET.SubElement(root, 'type').text = data.get('type', '')
        ET.SubElement(root, 'title').text = data.get('title', '')
        ET.SubElement(root, 'scraped_at').text = data.get('scraped_at', '')
        ET.SubElement(root, 'is_insurance').text = str(data.get('is_insurance', False))
        
        # Add description if HTML
        if data.get('type') == 'html':
            ET.SubElement(root, 'description').text = data.get('description', '')
            
            # Add content
            content_elem = ET.SubElement(root, 'content')
            content = data.get('content', {})
            
            # Headings
            headings_elem = ET.SubElement(content_elem, 'headings')
            for heading in content.get('headings', []):
                h_elem = ET.SubElement(headings_elem, 'heading')
                h_elem.set('level', heading['level'])
                h_elem.text = heading['text']
            
            # Paragraphs
            paragraphs_elem = ET.SubElement(content_elem, 'paragraphs')
            for para in content.get('paragraphs', []):
                ET.SubElement(paragraphs_elem, 'paragraph').text = para
            
            # Lists
            lists_elem = ET.SubElement(content_elem, 'lists')
            for lst in content.get('lists', []):
                list_elem = ET.SubElement(lists_elem, 'list')
                list_elem.set('type', lst['type'])
                for item in lst['items']:
                    ET.SubElement(list_elem, 'item').text = item
            
            # Tables
            tables_elem = ET.SubElement(content_elem, 'tables')
            for table in content.get('tables', []):
                table_elem = ET.SubElement(tables_elem, 'table')
                for row in table:
                    row_elem = ET.SubElement(table_elem, 'row')
                    for cell in row:
                        ET.SubElement(row_elem, 'cell').text = cell
            
            # Contact info
            if content.get('contact_info'):
                contact_elem = ET.SubElement(content_elem, 'contact_info')
                for phone in content['contact_info'].get('phones', []):
                    ET.SubElement(contact_elem, 'phone').text = phone
                for email in content['contact_info'].get('emails', []):
                    ET.SubElement(contact_elem, 'email').text = email
            
            # Links
            links_elem = ET.SubElement(root, 'links')
            for link in data.get('links', []):
                link_elem = ET.SubElement(links_elem, 'link')
                link_elem.set('href', link['url'])
                link_elem.set('is_pdf', str(link.get('is_pdf', False)))
                link_elem.text = link['text']
        
        # PDF content
        elif data.get('type') == 'pdf':
            pdf_content = data.get('content', {})
            
            # Metadata
            metadata_elem = ET.SubElement(root, 'pdf_metadata')
            for key, value in pdf_content.get('metadata', {}).items():
                ET.SubElement(metadata_elem, key).text = str(value)
            
            # Full text
            ET.SubElement(root, 'full_text').text = pdf_content.get('text', '')
            
            # Pages
            pages_elem = ET.SubElement(root, 'pages')
            for page in pdf_content.get('pages', []):
                page_elem = ET.SubElement(pages_elem, 'page')
                page_elem.set('number', str(page['page_number']))
                page_elem.text = page['text']
            
            # Tables
            if pdf_content.get('tables'):
                tables_elem = ET.SubElement(root, 'extracted_tables')
                for table in pdf_content['tables']:
                    table_elem = ET.SubElement(tables_elem, 'table')
                    table_elem.set('page', str(table['page']))
                    for row in table['data']:
                        row_elem = ET.SubElement(table_elem, 'row')
                        for cell in row:
                            ET.SubElement(row_elem, 'cell').text = str(cell) if cell else ''
        
        # Pretty print XML
        xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        logger.info(f"Saved XML: {filename}")

    def crawl(self, max_depth: int = 3):
        """Crawl CMU health websites"""
        to_visit = [(url, 0) for url in self.start_urls]
        
        while to_visit:
            url, depth = to_visit.pop(0)
            
            if depth > max_depth:
                continue
            
            if url in self.visited_urls:
                continue
            
            # Check if URL is allowed
            parsed = urlparse(url)
            if not any(domain in parsed.netloc + parsed.path for domain in self.allowed_domains):
                continue
            
            # Scrape page
            data = self.scrape_page(url)
            
            if data:
                # Generate filename
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                
                if data.get('is_insurance'):
                    filename = os.path.join(self.output_dir, "insurance", f"{url_hash}.xml")
                else:
                    filename = os.path.join(self.output_dir, "pages", f"{url_hash}.xml")
                
                self.save_to_xml(data, filename)
                
                # Add new URLs to visit
                if data.get('type') == 'html':
                    for link in data.get('links', []):
                        link_url = link['url']
                        if link_url not in self.visited_urls:
                            # Prioritize PDFs and insurance pages
                            if link.get('is_pdf') or any(kw in link_url.lower() for kw in self.insurance_keywords):
                                to_visit.insert(0, (link_url, depth + 1))
                            else:
                                to_visit.append((link_url, depth + 1))
            
            # Be polite
            time.sleep(0.5)

    def generate_summary(self):
        """Generate summary of scraped data"""
        summary = {
            'total_pages': len(self.visited_urls),
            'total_pdfs': len(self.pdf_urls),
            'failed_urls': list(self.failed_urls),
            'insurance_pages': 0,
            'pdf_list': list(self.pdf_urls)
        }
        
        # Count insurance pages
        insurance_dir = os.path.join(self.output_dir, "insurance")
        if os.path.exists(insurance_dir):
            summary['insurance_pages'] = len(os.listdir(insurance_dir))
        
        # Save summary
        summary_path = os.path.join(self.output_dir, "summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Scraping complete! Summary saved to {summary_path}")
        logger.info(f"Total pages: {summary['total_pages']}")
        logger.info(f"Total PDFs: {summary['total_pdfs']}")
        logger.info(f"Insurance pages: {summary['insurance_pages']}")

def main():
    scraper = EnhancedCMUHealthScraper()
    logger.info("Starting enhanced CMU Health Services scraping...")
    
    try:
        scraper.crawl(max_depth=3)
        scraper.generate_summary()
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Scraping session ended")

if __name__ == "__main__":
    main()