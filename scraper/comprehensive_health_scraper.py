#!/usr/bin/env python3
"""
Comprehensive CMU Health Services Website Scraper
Extracts ALL content from https://www.cmu.edu/health-services/index.html
and all linked pages, ensuring nothing is missed.
"""

import os
import sys
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib
import logging
from datetime import datetime
import re
from typing import Dict, List, Set, Optional, Tuple
import pdfplumber
import PyPDF2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_scrape.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveCMUHealthScraper:
    def __init__(self, output_dir: str = "comprehensive_health_data"):
        self.output_dir = output_dir
        self.base_url = "https://www.cmu.edu/health-services/"
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.pdf_urls: Set[str] = set()
        self.all_pages_data: List[Dict] = []
        
        # Session for consistent requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "pages"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "pdfs"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "json"), exist_ok=True)
        
        # Important sections to ensure we capture
        self.critical_sections = [
            'services', 'appointments', 'insurance', 'billing', 'pharmacy',
            'immunizations', 'forms', 'resources', 'about', 'contact',
            'hours', 'location', 'emergency', 'mental-health', 'counseling',
            'wellness', 'health-education', 'travel', 'international',
            'new-students', 'leaving-cmu', 'staff', 'policies', 'faqs'
        ]
        
    def is_health_services_url(self, url: str) -> bool:
        """Check if URL belongs to CMU health services"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Include various health-related CMU domains
        health_domains = [
            'health-services',
            'counseling',
            'wellness',
            'health',
            'uhs',  # University Health Services
            'caps'  # Counseling and Psychological Services
        ]
        
        return any(domain in path for domain in health_domains)
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL to avoid duplicates"""
        # Remove fragments
        url = url.split('#')[0]
        # Remove trailing slashes
        url = url.rstrip('/')
        # Remove common tracking parameters
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        # Keep only essential parameters
        essential_params = ['id', 'page', 'section']
        filtered_params = {k: v for k, v in query_params.items() if k in essential_params}
        
        if filtered_params:
            from urllib.parse import urlencode
            new_query = urlencode(filtered_params, doseq=True)
            url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
        else:
            url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        return url
    
    def extract_all_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all links from a page"""
        links = []
        
        # Find all anchor tags
        for tag in soup.find_all(['a', 'area']):
            href = tag.get('href')
            if href:
                absolute_url = urljoin(current_url, href)
                normalized = self.normalize_url(absolute_url)
                
                # Check if it's a health services URL or PDF
                if self.is_health_services_url(normalized) or normalized.endswith('.pdf'):
                    links.append(normalized)
        
        # Also check for links in JavaScript
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for URLs in JavaScript
                url_pattern = r'(?:href|url|link)\s*[=:]\s*["\']([^"\']+)["\']'
                matches = re.findall(url_pattern, script.string)
                for match in matches:
                    if match.startswith('/') or 'health' in match:
                        absolute_url = urljoin(current_url, match)
                        normalized = self.normalize_url(absolute_url)
                        if self.is_health_services_url(normalized):
                            links.append(normalized)
        
        # Check meta refresh tags
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            content = meta_refresh.get('content', '')
            match = re.search(r'url=(.+)', content, re.IGNORECASE)
            if match:
                refresh_url = urljoin(current_url, match.group(1))
                links.append(self.normalize_url(refresh_url))
        
        return list(set(links))  # Remove duplicates
    
    def extract_page_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract comprehensive content from a page"""
        content = {
            'url': url,
            'title': '',
            'description': '',
            'main_content': '',
            'sections': {},
            'contact_info': {},
            'hours': {},
            'services': [],
            'important_info': [],
            'forms': [],
            'resources': [],
            'metadata': {},
            'scraped_at': datetime.now().isoformat()
        }
        
        # Title
        title = soup.find('title')
        if title:
            content['title'] = title.text.strip()
        
        # Meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            content['description'] = meta_desc.get('content', '')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Main content areas
        main_selectors = [
            'main', 'article', '.content', '#content', '.main-content',
            '[role="main"]', '.page-content', '#main-content'
        ]
        
        main_content = None
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Extract text content
            content['main_content'] = main_content.get_text(separator='\n', strip=True)
            
            # Extract sections
            for i, section in enumerate(['section', 'article', 'div']):
                for j, elem in enumerate(main_content.find_all(section)):
                    section_id = elem.get('id', f'{section}_{i}_{j}')
                    section_class = ' '.join(elem.get('class', []))
                    
                    # Check if this is an important section
                    if any(keyword in (section_id + section_class).lower() for keyword in self.critical_sections):
                        content['sections'][section_id] = {
                            'html': str(elem),
                            'text': elem.get_text(separator='\n', strip=True),
                            'links': [urljoin(url, a.get('href')) for a in elem.find_all('a', href=True)]
                        }
            
            # Extract contact information
            self._extract_contact_info(main_content, content)
            
            # Extract hours
            self._extract_hours(main_content, content)
            
            # Extract services
            self._extract_services(main_content, content)
            
            # Extract forms
            self._extract_forms(main_content, content, url)
            
            # Extract important notices
            self._extract_important_info(main_content, content)
        
        # Extract all text for search
        content['full_text'] = soup.get_text(separator='\n', strip=True)
        
        return content
    
    def _extract_contact_info(self, soup: BeautifulSoup, content: Dict):
        """Extract contact information"""
        # Phone numbers
        phone_pattern = re.compile(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})')
        phones = phone_pattern.findall(soup.get_text())
        content['contact_info']['phones'] = list(set(phones))
        
        # Email addresses
        email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        emails = email_pattern.findall(soup.get_text())
        content['contact_info']['emails'] = list(set(emails))
        
        # Addresses
        address_keywords = ['avenue', 'street', 'ave', 'st', 'road', 'rd', 'pittsburgh', 'pa']
        text_lines = soup.get_text().split('\n')
        addresses = []
        for line in text_lines:
            if any(keyword in line.lower() for keyword in address_keywords):
                addresses.append(line.strip())
        content['contact_info']['addresses'] = addresses[:5]  # Limit to 5
    
    def _extract_hours(self, soup: BeautifulSoup, content: Dict):
        """Extract hours of operation"""
        hours_keywords = ['hours', 'open', 'closed', 'monday', 'tuesday', 'wednesday', 
                         'thursday', 'friday', 'saturday', 'sunday', 'am', 'pm']
        
        hours_sections = []
        for elem in soup.find_all(['p', 'div', 'li', 'td']):
            text = elem.get_text().lower()
            if any(keyword in text for keyword in hours_keywords):
                hours_sections.append(elem.get_text(strip=True))
        
        content['hours']['extracted'] = hours_sections[:10]  # Limit to 10
    
    def _extract_services(self, soup: BeautifulSoup, content: Dict):
        """Extract services offered"""
        services_keywords = ['service', 'offer', 'provide', 'available', 'treatment']
        
        # Look for lists that might contain services
        for ul in soup.find_all(['ul', 'ol']):
            parent_text = ''
            if ul.parent:
                prev = ul.find_previous_sibling(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
                if prev:
                    parent_text = prev.get_text().lower()
            
            if any(keyword in parent_text for keyword in services_keywords):
                services = [li.get_text(strip=True) for li in ul.find_all('li')]
                content['services'].extend(services)
    
    def _extract_forms(self, soup: BeautifulSoup, content: Dict, base_url: str):
        """Extract forms and documents"""
        # Find all links to forms
        form_keywords = ['form', 'document', 'pdf', 'download', 'fillable']
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text().lower()
            
            if any(keyword in text or keyword in href.lower() for keyword in form_keywords):
                form_url = urljoin(base_url, href)
                content['forms'].append({
                    'title': link.get_text(strip=True),
                    'url': form_url,
                    'type': 'pdf' if href.endswith('.pdf') else 'link'
                })
    
    def _extract_important_info(self, soup: BeautifulSoup, content: Dict):
        """Extract important notices and alerts"""
        # Look for alert boxes, notices, etc.
        important_selectors = ['.alert', '.notice', '.warning', '.important', 
                             '[role="alert"]', '.announcement']
        
        for selector in important_selectors:
            for elem in soup.select(selector):
                content['important_info'].append(elem.get_text(strip=True))
        
        # Also look for text with important keywords
        important_keywords = ['important', 'notice', 'alert', 'warning', 'required', 'mandatory']
        for elem in soup.find_all(['p', 'div', 'li']):
            text = elem.get_text().lower()
            if any(keyword in text for keyword in important_keywords):
                content['important_info'].append(elem.get_text(strip=True))
    
    def download_pdf(self, url: str) -> Optional[Dict]:
        """Download and extract PDF content"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Save PDF
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = os.path.basename(urlparse(url).path) or f"document_{url_hash}.pdf"
            filepath = os.path.join(self.output_dir, "pdfs", filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Extract text
            pdf_content = {
                'url': url,
                'filename': filename,
                'filepath': filepath,
                'text': '',
                'metadata': {},
                'pages': []
            }
            
            # Try pdfplumber first
            try:
                with pdfplumber.open(filepath) as pdf:
                    pdf_content['metadata'] = pdf.metadata
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text() or ''
                        pdf_content['pages'].append({
                            'page_num': i + 1,
                            'text': page_text
                        })
                        pdf_content['text'] += page_text + '\n\n'
            except:
                # Fallback to PyPDF2
                with open(filepath, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for i, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        pdf_content['pages'].append({
                            'page_num': i + 1,
                            'text': page_text
                        })
                        pdf_content['text'] += page_text + '\n\n'
            
            logger.info(f"Successfully extracted PDF: {filename}")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Failed to download/extract PDF {url}: {e}")
            return None
    
    def scrape_page(self, url: str, depth: int = 0, max_depth: int = 5) -> Optional[Dict]:
        """Scrape a single page and its linked pages"""
        if url in self.visited_urls or depth > max_depth:
            return None
        
        self.visited_urls.add(url)
        logger.info(f"Scraping (depth={depth}): {url}")
        
        try:
            # Handle PDFs
            if url.endswith('.pdf'):
                self.pdf_urls.add(url)
                return self.download_pdf(url)
            
            # Handle HTML pages
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'application/pdf' in content_type:
                self.pdf_urls.add(url)
                return self.download_pdf(url)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract content
            page_data = self.extract_page_content(soup, url)
            
            # Find all links
            links = self.extract_all_links(soup, url)
            page_data['links'] = links
            
            # Save page data
            self.save_page_data(page_data)
            self.all_pages_data.append(page_data)
            
            # Recursively scrape linked pages
            for link in links:
                if link not in self.visited_urls:
                    time.sleep(0.5)  # Be polite
                    self.scrape_page(link, depth + 1, max_depth)
            
            return page_data
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            self.failed_urls.add(url)
            return None
    
    def save_page_data(self, data: Dict):
        """Save individual page data"""
        url_hash = hashlib.md5(data['url'].encode()).hexdigest()[:8]
        filename = f"page_{url_hash}.json"
        filepath = os.path.join(self.output_dir, "json", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def scrape_all_health_services(self):
        """Main method to scrape all health services content"""
        logger.info("Starting comprehensive health services scrape...")
        
        # Start with the main page
        main_url = "https://www.cmu.edu/health-services/index.html"
        self.scrape_page(main_url)
        
        # Also explicitly scrape critical sections
        critical_urls = [
            "https://www.cmu.edu/health-services/services/index.html",
            "https://www.cmu.edu/health-services/appointments/index.html",
            "https://www.cmu.edu/health-services/insurance/index.html",
            "https://www.cmu.edu/health-services/billing/index.html",
            "https://www.cmu.edu/health-services/pharmacy/index.html",
            "https://www.cmu.edu/health-services/immunizations/index.html",
            "https://www.cmu.edu/health-services/forms/index.html",
            "https://www.cmu.edu/health-services/resources/index.html",
            "https://www.cmu.edu/health-services/about/index.html",
            "https://www.cmu.edu/health-services/contact/index.html",
            "https://www.cmu.edu/counseling/",
            "https://www.cmu.edu/wellness/"
        ]
        
        for url in critical_urls:
            if url not in self.visited_urls:
                time.sleep(1)
                self.scrape_page(url)
        
        # Save comprehensive summary
        self.save_comprehensive_summary()
    
    def save_comprehensive_summary(self):
        """Save a comprehensive summary of all scraped data"""
        summary = {
            'scrape_date': datetime.now().isoformat(),
            'total_pages': len(self.visited_urls),
            'total_pdfs': len(self.pdf_urls),
            'failed_urls': list(self.failed_urls),
            'all_urls': list(self.visited_urls),
            'pdf_urls': list(self.pdf_urls),
            'statistics': {
                'pages_with_services': sum(1 for p in self.all_pages_data if p.get('services')),
                'pages_with_hours': sum(1 for p in self.all_pages_data if p.get('hours', {}).get('extracted')),
                'pages_with_contact': sum(1 for p in self.all_pages_data if p.get('contact_info', {}).get('phones')),
                'total_forms': sum(len(p.get('forms', [])) for p in self.all_pages_data)
            }
        }
        
        # Save summary
        summary_path = os.path.join(self.output_dir, "scrape_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        # Create a consolidated file for RAG ingestion
        self.create_rag_ready_file()
        
        logger.info(f"Scraping complete! Summary saved to {summary_path}")
        logger.info(f"Total pages: {summary['total_pages']}")
        logger.info(f"Total PDFs: {summary['total_pdfs']}")
        logger.info(f"Failed URLs: {len(summary['failed_urls'])}")
    
    def create_rag_ready_file(self):
        """Create a file ready for RAG ingestion"""
        rag_documents = []
        
        for page_data in self.all_pages_data:
            # Create a comprehensive text representation
            content_parts = [
                f"Title: {page_data.get('title', 'No Title')}",
                f"URL: {page_data.get('url', '')}",
                f"Description: {page_data.get('description', '')}",
                "",
                "Main Content:",
                page_data.get('main_content', ''),
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
            
            # Add important info
            if page_data.get('important_info'):
                content_parts.append("Important Information:")
                content_parts.extend(page_data['important_info'])
                content_parts.append("")
            
            # Add forms
            if page_data.get('forms'):
                content_parts.append("Available Forms:")
                for form in page_data['forms']:
                    content_parts.append(f"- {form['title']} ({form['url']})")
                content_parts.append("")
            
            # Create document for RAG
            rag_doc = {
                'content': '\n'.join(content_parts),
                'metadata': {
                    'source': 'CMU Health Services Website',
                    'url': page_data.get('url', ''),
                    'title': page_data.get('title', ''),
                    'type': 'webpage',
                    'scraped_at': page_data.get('scraped_at', ''),
                    'has_services': bool(page_data.get('services')),
                    'has_hours': bool(page_data.get('hours', {}).get('extracted')),
                    'has_contact': bool(page_data.get('contact_info', {}).get('phones'))
                }
            }
            
            rag_documents.append(rag_doc)
        
        # Save RAG-ready file
        rag_file_path = os.path.join(self.output_dir, "health_services_for_rag.json")
        with open(rag_file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'documents': rag_documents,
                'metadata': {
                    'source': 'CMU Health Services Comprehensive Scrape',
                    'scrape_date': datetime.now().isoformat(),
                    'total_documents': len(rag_documents)
                }
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"RAG-ready file saved to {rag_file_path}")

def main():
    scraper = ComprehensiveCMUHealthScraper()
    scraper.scrape_all_health_services()

if __name__ == "__main__":
    main()