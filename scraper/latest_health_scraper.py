#!/usr/bin/env python3
"""
Enhanced CMU Health Services Website Scraper
Scrapes the latest information from https://www.cmu.edu/health-services/
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse
import hashlib
import os
from datetime import datetime
import re

class CMUHealthServicesScraper:
    def __init__(self):
        self.base_url = "https://www.cmu.edu/health-services/"
        self.visited_urls = set()
        self.scraped_data = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def scrape_all(self):
        """Main method to scrape all health services pages"""
        print(f"Starting comprehensive scrape of {self.base_url}")
        
        # Start with the main page
        self.scrape_page(self.base_url)
        
        # Key pages to ensure we capture
        important_pages = [
            "services/index.html",
            "services/primary-care/index.html",
            "services/counseling-psychological-services/index.html",
            "appointment/index.html",
            "insurance/index.html",
            "hours-locations/index.html",
            "services/pharmacy/index.html",
            "services/immunizations/index.html",
            "services/radiology-and-laboratory/index.html",
            "services/nutrition/index.html",
            "services/physical-therapy/index.html",
            "services/wellness/index.html",
            "billing-insurance/index.html",
            "patient-rights/index.html",
            "forms/index.html",
            "resources/index.html",
            "emergencies/index.html",
            "staff/index.html",
            "news/index.html"
        ]
        
        for page in important_pages:
            url = urljoin(self.base_url, page)
            if url not in self.visited_urls:
                print(f"Scraping important page: {url}")
                self.scrape_page(url)
                time.sleep(0.5)  # Be respectful
        
        return self.scraped_data
    
    def scrape_page(self, url, depth=0, max_depth=3):
        """Scrape a single page and follow links"""
        if url in self.visited_urls or depth > max_depth:
            return
        
        # Only scrape pages within the health services domain
        if not url.startswith(self.base_url):
            return
            
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract page data
            page_data = {
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'title': self.extract_title(soup),
                'content': self.extract_content(soup),
                'meta_description': self.extract_meta_description(soup),
                'navigation': self.extract_navigation(soup),
                'contact_info': self.extract_contact_info(soup),
                'hours': self.extract_hours(soup),
                'services': self.extract_services(soup),
                'announcements': self.extract_announcements(soup),
                'forms_and_resources': self.extract_forms_and_resources(soup)
            }
            
            # Generate unique ID
            page_data['id'] = hashlib.md5(url.encode()).hexdigest()[:8]
            
            self.scraped_data.append(page_data)
            print(f"Successfully scraped: {url}")
            
            # Follow links on the page
            if depth < max_depth:
                links = soup.find_all('a', href=True)
                for link in links:
                    next_url = urljoin(url, link['href'])
                    if self.is_valid_url(next_url):
                        self.scrape_page(next_url, depth + 1, max_depth)
                        time.sleep(0.3)
                        
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
    
    def is_valid_url(self, url):
        """Check if URL should be scraped"""
        # Skip non-health-services pages, PDFs, images, etc.
        if not url.startswith(self.base_url):
            return False
        if any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.doc', '.docx', '.zip']):
            return False
        if '#' in url:  # Skip anchors
            return False
        return True
    
    def extract_title(self, soup):
        """Extract page title"""
        title = soup.find('title')
        if title:
            return title.get_text(strip=True)
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
            
        return "Untitled Page"
    
    def extract_meta_description(self, soup):
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            return meta.get('content', '')
        return ''
    
    def extract_content(self, soup):
        """Extract main content from the page"""
        content_sections = []
        
        # Try to find main content area
        main_content = soup.find('div', class_='content') or \
                      soup.find('main') or \
                      soup.find('div', id='content') or \
                      soup.find('article')
        
        if main_content:
            # Extract all text content
            for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'span']):
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Filter out very short text
                    content_sections.append({
                        'type': element.name,
                        'text': text
                    })
        
        return content_sections
    
    def extract_navigation(self, soup):
        """Extract navigation menu items"""
        nav_items = []
        
        # Look for navigation elements
        nav = soup.find('nav') or soup.find('div', class_='navigation')
        if nav:
            links = nav.find_all('a')
            for link in links:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                if text and href:
                    nav_items.append({
                        'text': text,
                        'url': urljoin(self.base_url, href)
                    })
        
        return nav_items
    
    def extract_contact_info(self, soup):
        """Extract contact information"""
        contact_info = {}
        
        # Look for phone numbers
        phone_pattern = re.compile(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})')
        phones = phone_pattern.findall(soup.get_text())
        if phones:
            contact_info['phones'] = list(set(phones))
        
        # Look for email addresses
        email_pattern = re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
        emails = email_pattern.findall(soup.get_text())
        if emails:
            contact_info['emails'] = list(set(emails))
        
        # Look for addresses
        address_keywords = ['Morewood', 'Avenue', 'Pittsburgh', 'PA', '15213']
        text = soup.get_text()
        for keyword in address_keywords:
            if keyword in text:
                # Try to extract surrounding text as address
                idx = text.find(keyword)
                start = max(0, idx - 50)
                end = min(len(text), idx + 100)
                potential_address = text[start:end].strip()
                if 'address' not in contact_info:
                    contact_info['address'] = potential_address
                break
        
        return contact_info
    
    def extract_hours(self, soup):
        """Extract hours of operation"""
        hours = []
        
        # Look for common patterns
        hour_patterns = [
            re.compile(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[^:]*:\s*([0-9:\s\-apmAPM]+)'),
            re.compile(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[^:]*:\s*([0-9:\s\-apmAPM]+)'),
            re.compile(r'Hours[^:]*:\s*([^<\n]+)'),
        ]
        
        text = soup.get_text()
        for pattern in hour_patterns:
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, tuple):
                    hours.append(f"{match[0]}: {match[1]}")
                else:
                    hours.append(match)
        
        return list(set(hours))  # Remove duplicates
    
    def extract_services(self, soup):
        """Extract services offered"""
        services = []
        
        # Look for service listings
        service_sections = soup.find_all(['div', 'section'], class_=re.compile('service'))
        for section in service_sections:
            service_name = section.find(['h2', 'h3', 'h4'])
            if service_name:
                service_desc = section.find('p')
                services.append({
                    'name': service_name.get_text(strip=True),
                    'description': service_desc.get_text(strip=True) if service_desc else ''
                })
        
        # Also look for lists of services
        for ul in soup.find_all('ul'):
            # Check if this looks like a service list
            if any(keyword in str(ul).lower() for keyword in ['service', 'care', 'treatment']):
                for li in ul.find_all('li'):
                    service_text = li.get_text(strip=True)
                    if service_text and len(service_text) > 5:
                        services.append({
                            'name': service_text,
                            'description': ''
                        })
        
        return services
    
    def extract_announcements(self, soup):
        """Extract any announcements or alerts"""
        announcements = []
        
        # Look for alert/announcement sections
        alert_classes = ['alert', 'announcement', 'notice', 'update', 'news-item']
        for class_name in alert_classes:
            alerts = soup.find_all(['div', 'section'], class_=re.compile(class_name))
            for alert in alerts:
                text = alert.get_text(strip=True)
                if text:
                    announcements.append(text)
        
        return announcements
    
    def extract_forms_and_resources(self, soup):
        """Extract downloadable forms and resources"""
        resources = []
        
        # Look for PDF links and forms
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx']):
                resources.append({
                    'name': text,
                    'url': urljoin(self.base_url, href),
                    'type': 'document'
                })
        
        return resources
    
    def save_results(self, output_dir='scraped_latest'):
        """Save scraped data to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save individual pages
        for page_data in self.scraped_data:
            filename = f"{output_dir}/{page_data['id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)
        
        # Save summary
        summary = {
            'scrape_date': datetime.now().isoformat(),
            'total_pages': len(self.scraped_data),
            'base_url': self.base_url,
            'pages': [
                {
                    'id': p['id'],
                    'url': p['url'],
                    'title': p['title']
                } for p in self.scraped_data
            ]
        }
        
        with open(f"{output_dir}/summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(self.scraped_data)} pages to {output_dir}/")
        
        # Create a combined markdown file for easy ingestion
        self.create_combined_markdown(output_dir)
    
    def create_combined_markdown(self, output_dir):
        """Create a combined markdown file with all scraped content"""
        markdown_content = f"""# CMU University Health Services - Complete Information
*Last Updated: {datetime.now().strftime('%B %d, %Y')}*
*Source: https://www.cmu.edu/health-services/*

---

"""
        
        for page_data in self.scraped_data:
            markdown_content += f"\n## {page_data['title']}\n"
            markdown_content += f"*URL: {page_data['url']}*\n\n"
            
            if page_data['meta_description']:
                markdown_content += f"{page_data['meta_description']}\n\n"
            
            # Add content sections
            for section in page_data['content']:
                if section['type'] in ['h1', 'h2', 'h3', 'h4']:
                    level = '#' * (int(section['type'][1]) + 1)
                    markdown_content += f"\n{level} {section['text']}\n\n"
                else:
                    markdown_content += f"{section['text']}\n\n"
            
            # Add contact info if available
            if page_data['contact_info']:
                markdown_content += "\n### Contact Information\n"
                if 'phones' in page_data['contact_info']:
                    markdown_content += f"- Phone: {', '.join(page_data['contact_info']['phones'])}\n"
                if 'emails' in page_data['contact_info']:
                    markdown_content += f"- Email: {', '.join(page_data['contact_info']['emails'])}\n"
                if 'address' in page_data['contact_info']:
                    markdown_content += f"- Address: {page_data['contact_info']['address']}\n"
                markdown_content += "\n"
            
            # Add hours if available
            if page_data['hours']:
                markdown_content += "\n### Hours of Operation\n"
                for hour in page_data['hours']:
                    markdown_content += f"- {hour}\n"
                markdown_content += "\n"
            
            # Add services if available
            if page_data['services']:
                markdown_content += "\n### Services\n"
                for service in page_data['services']:
                    markdown_content += f"- **{service['name']}**"
                    if service['description']:
                        markdown_content += f": {service['description']}"
                    markdown_content += "\n"
                markdown_content += "\n"
            
            markdown_content += "\n---\n"
        
        # Save the combined markdown
        with open(f"{output_dir}/cmu_health_services_complete.md", 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Created combined markdown file: {output_dir}/cmu_health_services_complete.md")


if __name__ == "__main__":
    scraper = CMUHealthServicesScraper()
    scraper.scrape_all()
    scraper.save_results()