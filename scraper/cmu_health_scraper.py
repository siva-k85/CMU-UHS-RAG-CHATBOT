#!/usr/bin/env python3
"""
CMU Health Services Website Scraper
Scrapes and processes health services information from CMU websites
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging
import hashlib
from typing import Dict, List, Set, Optional, Tuple
import re

class CMUHealthScraper:
    def __init__(self, base_url: str = "https://www.cmu.edu/health-services/", 
                 delay: float = 1.0, max_depth: int = 3):
        self.base_url = base_url
        self.delay = delay
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CMU-Health-Services-Bot/1.0 (Educational Purpose)'
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        self.output_dir = "scraped_data"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL should be scraped"""
        parsed = urlparse(url)
        
        # Only scrape CMU health-related pages
        valid_domains = ['cmu.edu']
        valid_paths = ['/health-services/', '/counseling/', '/health/', '/wellness/']
        
        if not any(domain in parsed.netloc for domain in valid_domains):
            return False
        
        if not any(path in parsed.path for path in valid_paths):
            return False
        
        # Skip non-HTML content
        skip_extensions = ['.pdf', '.jpg', '.png', '.gif', '.doc', '.docx', '.xls', '.xlsx']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        return True
    
    def extract_content(self, soup: BeautifulSoup) -> Dict:
        """Extract relevant content from the page"""
        # Remove navigation, scripts, and styles
        for element in soup(['nav', 'script', 'style', 'header', 'footer']):
            element.decompose()
        
        # Extract title
        title = soup.find('title')
        title_text = title.text.strip() if title else "CMU Health Services"
        
        # Extract main content
        main_content = soup.find('main') or soup.find('div', {'class': ['content', 'main-content']})
        if not main_content:
            main_content = soup.find('body')
        
        # Clean and extract text
        content_text = main_content.get_text(separator='\n', strip=True) if main_content else ""
        
        # Extract specific information
        extracted_info = {
            'phone_numbers': self.extract_phone_numbers(content_text),
            'emails': self.extract_emails(content_text),
            'hours': self.extract_hours(content_text),
            'addresses': self.extract_addresses(content_text),
            'services': self.extract_services(soup)
        }
        
        return {
            'title': title_text,
            'content': content_text,
            'extracted_info': extracted_info,
            'html_structure': self.extract_structured_data(soup)
        }
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phone_pattern = r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\(\d{3}\)\s*\d{3}[-.\s]?\d{4})'
        phones = re.findall(phone_pattern, text)
        return list(set(phones))
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))
    
    def extract_hours(self, text: str) -> List[str]:
        """Extract operating hours from text"""
        hours_patterns = [
            r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[\s-]+\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)[\s-]+\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)',
            r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)[\s-]+\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)',
            r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[\s-]+\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)'
        ]
        
        hours = []
        for pattern in hours_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            hours.extend(matches)
        
        return list(set(hours))
    
    def extract_addresses(self, text: str) -> List[str]:
        """Extract addresses from text"""
        # Simple pattern for Pittsburgh addresses
        address_pattern = r'\d+\s+\w+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)(?:,\s*Pittsburgh)?(?:,\s*PA)?(?:\s+\d{5})?'
        addresses = re.findall(address_pattern, text, re.IGNORECASE)
        return list(set(addresses))
    
    def extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract list of services offered"""
        services = []
        
        # Look for service lists
        service_sections = soup.find_all(['ul', 'ol'], class_=re.compile('services|offerings', re.I))
        for section in service_sections:
            items = section.find_all('li')
            services.extend([item.get_text(strip=True) for item in items])
        
        # Look for service headings
        service_headings = soup.find_all(['h2', 'h3'], string=re.compile('services|we offer|available', re.I))
        for heading in service_headings:
            next_sibling = heading.find_next_sibling()
            if next_sibling and next_sibling.name in ['ul', 'ol']:
                items = next_sibling.find_all('li')
                services.extend([item.get_text(strip=True) for item in items])
        
        return list(set(services))
    
    def extract_structured_data(self, soup: BeautifulSoup) -> Dict:
        """Extract structured data like FAQs, contact info sections"""
        structured_data = {}
        
        # Extract FAQs
        faq_section = soup.find('div', class_=re.compile('faq', re.I))
        if faq_section:
            faqs = []
            questions = faq_section.find_all(['h3', 'h4', 'dt'])
            for q in questions:
                answer = q.find_next_sibling(['p', 'dd'])
                if answer:
                    faqs.append({
                        'question': q.get_text(strip=True),
                        'answer': answer.get_text(strip=True)
                    })
            structured_data['faqs'] = faqs
        
        # Extract contact sections
        contact_section = soup.find(['div', 'section'], class_=re.compile('contact', re.I))
        if contact_section:
            structured_data['contact_info'] = contact_section.get_text(strip=True)
        
        return structured_data
    
    def categorize_page(self, url: str, content: Dict) -> str:
        """Categorize the page based on URL and content"""
        url_lower = url.lower()
        content_lower = content.get('content', '').lower()
        
        if 'appointment' in url_lower or 'scheduling' in content_lower:
            return 'appointments'
        elif 'insurance' in url_lower or 'billing' in content_lower:
            return 'insurance'
        elif 'hour' in url_lower or 'location' in content_lower:
            return 'hours_location'
        elif 'service' in url_lower or 'treatment' in content_lower:
            return 'services'
        elif 'emergency' in url_lower or 'urgent' in content_lower:
            return 'emergency'
        elif 'counseling' in url_lower or 'mental' in content_lower:
            return 'mental_health'
        elif 'pharmacy' in url_lower:
            return 'pharmacy'
        else:
            return 'general'
    
    def scrape_page(self, url: str, depth: int = 0) -> Optional[Dict]:
        """Scrape a single page"""
        if url in self.visited_urls or depth > self.max_depth:
            return None
        
        self.visited_urls.add(url)
        
        try:
            self.logger.info(f"Scraping: {url} (depth: {depth})")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content = self.extract_content(soup)
            
            # Create page data
            page_data = {
                'url': url,
                'title': content['title'],
                'content': content['content'],
                'extracted_info': content['extracted_info'],
                'category': self.categorize_page(url, content),
                'timestamp': datetime.now().isoformat(),
                'depth': depth
            }
            
            # Save individual page
            self.save_page_data(page_data)
            self.scraped_data.append(page_data)
            
            # Find and queue child links
            if depth < self.max_depth:
                links = soup.find_all('a', href=True)
                child_urls = []
                
                for link in links:
                    child_url = urljoin(url, link['href'])
                    if self.is_valid_url(child_url) and child_url not in self.visited_urls:
                        child_urls.append(child_url)
                
                # Scrape child pages
                for child_url in child_urls:
                    time.sleep(self.delay)  # Be respectful
                    self.scrape_page(child_url, depth + 1)
            
            return page_data
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def save_page_data(self, page_data: Dict):
        """Save individual page data"""
        # Create filename from URL
        url_hash = hashlib.md5(page_data['url'].encode()).hexdigest()[:8]
        filename = f"{page_data['category']}_{url_hash}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)
    
    def run(self):
        """Run the scraper"""
        self.logger.info(f"Starting scrape of {self.base_url}")
        start_time = time.time()
        
        # Start scraping from base URL
        self.scrape_page(self.base_url)
        
        # Save summary
        summary = {
            'total_pages': len(self.scraped_data),
            'categories': {},
            'base_url': self.base_url,
            'scrape_time': time.time() - start_time,
            'timestamp': datetime.now().isoformat()
        }
        
        # Count pages by category
        for page in self.scraped_data:
            category = page['category']
            summary['categories'][category] = summary['categories'].get(category, 0) + 1
        
        # Save summary
        summary_path = os.path.join(self.output_dir, 'scrape_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Scraping completed. Scraped {len(self.scraped_data)} pages in {summary['scrape_time']:.2f} seconds")
        
        # Generate markdown export
        self.export_to_markdown()
        
        return summary
    
    def export_to_markdown(self):
        """Export scraped data to markdown format for easy reading"""
        export_dir = os.path.join(self.output_dir, 'markdown_export')
        os.makedirs(export_dir, exist_ok=True)
        
        for page_data in self.scraped_data:
            # Create markdown content
            md_content = f"# {page_data['title']}\n\n"
            md_content += f"**URL:** {page_data['url']}\n"
            md_content += f"**Category:** {page_data['category']}\n"
            md_content += f"**Scraped:** {page_data['timestamp']}\n\n"
            
            # Add extracted info
            extracted = page_data['extracted_info']
            if extracted.get('phone_numbers'):
                md_content += f"**Phone Numbers:** {', '.join(extracted['phone_numbers'])}\n"
            if extracted.get('emails'):
                md_content += f"**Emails:** {', '.join(extracted['emails'])}\n"
            if extracted.get('hours'):
                md_content += f"**Hours:** {'; '.join(extracted['hours'])}\n"
            if extracted.get('addresses'):
                md_content += f"**Addresses:** {'; '.join(extracted['addresses'])}\n"
            
            md_content += "\n---\n\n"
            md_content += page_data['content']
            
            # Save markdown file
            url_hash = hashlib.md5(page_data['url'].encode()).hexdigest()[:8]
            filename = f"{page_data['category']}_{url_hash}.md"
            filepath = os.path.join(export_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)

if __name__ == "__main__":
    scraper = CMUHealthScraper()
    scraper.run()