#!/usr/bin/env python3
"""
Utility functions for the CMU Health Services scraper
"""

import os
import json
import csv
from typing import List, Dict, Optional, Union
from datetime import datetime
import hashlib
import re
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class ScraperUtils:
    """Utility functions for web scraping"""
    
    @staticmethod
    def create_url_hash(url: str) -> str:
        """
        Create a hash from URL for deduplication
        
        Args:
            url: URL to hash
            
        Returns:
            MD5 hash of the URL
        """
        return hashlib.md5(url.encode()).hexdigest()
        
    @staticmethod
    def extract_domain_info(url: str) -> Dict[str, str]:
        """
        Extract domain information from URL
        
        Args:
            url: URL to parse
            
        Returns:
            Dictionary with domain information
        """
        parsed = urlparse(url)
        return {
            'scheme': parsed.scheme,
            'domain': parsed.netloc,
            'path': parsed.path,
            'params': parsed.params,
            'query': parsed.query,
            'fragment': parsed.fragment,
            'full_domain': f"{parsed.scheme}://{parsed.netloc}"
        }
        
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace in text
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
        
    @staticmethod
    def extract_structured_data(content: str) -> Dict[str, List[str]]:
        """
        Extract structured data like lists, tables from content
        
        Args:
            content: HTML content
            
        Returns:
            Dictionary with structured data
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        structured_data = {
            'lists': [],
            'tables': [],
            'definitions': []
        }
        
        # Extract lists
        for list_tag in soup.find_all(['ul', 'ol']):
            list_items = []
            for li in list_tag.find_all('li'):
                list_items.append(li.get_text(strip=True))
            if list_items:
                structured_data['lists'].append(list_items)
                
        # Extract tables
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text(strip=True))
                if row_data:
                    table_data.append(row_data)
            if table_data:
                structured_data['tables'].append(table_data)
                
        # Extract definition lists
        for dl in soup.find_all('dl'):
            definitions = []
            current_term = None
            for child in dl.children:
                if child.name == 'dt':
                    current_term = child.get_text(strip=True)
                elif child.name == 'dd' and current_term:
                    definitions.append({
                        'term': current_term,
                        'definition': child.get_text(strip=True)
                    })
            if definitions:
                structured_data['definitions'].extend(definitions)
                
        return structured_data


class DataExporter:
    """Export scraped data in various formats"""
    
    @staticmethod
    def export_to_csv(data: List[Dict], filepath: str):
        """
        Export data to CSV format
        
        Args:
            data: List of dictionaries to export
            filepath: Output file path
        """
        if not data:
            logger.warning("No data to export")
            return
            
        # Get all unique keys
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
            
        # Remove complex fields that can't be easily represented in CSV
        simple_keys = [k for k in all_keys if not isinstance(data[0].get(k), (list, dict))]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(simple_keys))
            writer.writeheader()
            
            for item in data:
                # Create a filtered item with only simple values
                filtered_item = {k: v for k, v in item.items() if k in simple_keys}
                writer.writerow(filtered_item)
                
        logger.info(f"Exported {len(data)} items to {filepath}")
        
    @staticmethod
    def export_to_markdown(data: List[Dict], output_dir: str):
        """
        Export data to Markdown files
        
        Args:
            data: List of page data
            output_dir: Output directory
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Create index file
        index_path = os.path.join(output_dir, 'INDEX.md')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# CMU Health Services Content Index\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Pages by Category\n\n")
            
            # Group by category
            by_category = {}
            for item in data:
                category = item.get('category', 'general')
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(item)
                
            # Write category sections
            for category, items in sorted(by_category.items()):
                f.write(f"### {category.title()}\n\n")
                for item in items:
                    title = item.get('title', 'Untitled')
                    url = item.get('url', '')
                    filename = re.sub(r'[^\w\s-]', '', title)[:50]
                    f.write(f"- [{title}]({filename}.md) - [Source]({url})\n")
                f.write("\n")
                
        # Export individual pages
        for i, item in enumerate(data):
            title = item.get('title', f'Page {i+1}')
            filename = re.sub(r'[^\w\s-]', '', title)[:50]
            filepath = os.path.join(output_dir, f"{filename}.md")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"**Source:** {item.get('url', 'N/A')}\n")
                f.write(f"**Category:** {item.get('category', 'general')}\n")
                f.write(f"**Last Updated:** {item.get('scraped_at', 'Unknown')}\n\n")
                
                # Add metadata if available
                if 'meta_description' in item and item['meta_description']:
                    f.write(f"## Description\n\n{item['meta_description']}\n\n")
                    
                # Add main content
                f.write("## Content\n\n")
                content = item.get('content', item.get('cleaned_content', ''))
                f.write(content)
                
                # Add key information if available
                if 'key_information' in item:
                    key_info = item['key_information']
                    if any(key_info.values()):
                        f.write("\n\n## Key Information\n\n")
                        
                        if key_info.get('phone_numbers'):
                            f.write("**Phone Numbers:**\n")
                            for phone in key_info['phone_numbers']:
                                f.write(f"- {phone}\n")
                            f.write("\n")
                            
                        if key_info.get('email_addresses'):
                            f.write("**Email Addresses:**\n")
                            for email in key_info['email_addresses']:
                                f.write(f"- {email}\n")
                            f.write("\n")
                            
                        if key_info.get('addresses'):
                            f.write("**Addresses:**\n")
                            for address in key_info['addresses']:
                                f.write(f"- {address}\n")
                            f.write("\n")
                            
        logger.info(f"Exported {len(data)} pages to {output_dir}")
        
    @staticmethod
    def create_summary_report(data: List[Dict], filepath: str):
        """
        Create a summary report of the scraped data
        
        Args:
            data: Scraped data
            filepath: Output file path
        """
        report = {
            'summary': {
                'total_pages': len(data),
                'scrape_date': datetime.now().isoformat(),
                'categories': {}
            },
            'urls': [],
            'content_stats': {
                'total_words': 0,
                'avg_content_length': 0,
                'pages_with_phone': 0,
                'pages_with_email': 0
            }
        }
        
        total_length = 0
        
        for item in data:
            # Category count
            category = item.get('category', 'general')
            report['summary']['categories'][category] = \
                report['summary']['categories'].get(category, 0) + 1
                
            # URL list
            report['urls'].append({
                'url': item.get('url'),
                'title': item.get('title'),
                'category': category
            })
            
            # Content stats
            content = item.get('content', '')
            total_length += len(content)
            report['content_stats']['total_words'] += len(content.split())
            
            # Check for contact info
            if 'key_information' in item:
                if item['key_information'].get('phone_numbers'):
                    report['content_stats']['pages_with_phone'] += 1
                if item['key_information'].get('email_addresses'):
                    report['content_stats']['pages_with_email'] += 1
                    
        # Calculate averages
        if data:
            report['content_stats']['avg_content_length'] = total_length // len(data)
            
        # Save report
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Created summary report at {filepath}")


def validate_scraped_data(data: List[Dict]) -> Dict[str, List[str]]:
    """
    Validate scraped data for completeness and quality
    
    Args:
        data: Scraped data to validate
        
    Returns:
        Dictionary with validation results
    """
    issues = {
        'missing_title': [],
        'missing_content': [],
        'short_content': [],
        'duplicate_content': [],
        'missing_url': []
    }
    
    content_hashes = {}
    
    for i, item in enumerate(data):
        # Check for missing fields
        if not item.get('title'):
            issues['missing_title'].append(f"Item {i}: {item.get('url', 'Unknown URL')}")
            
        if not item.get('url'):
            issues['missing_url'].append(f"Item {i}")
            
        content = item.get('content', '')
        if not content:
            issues['missing_content'].append(f"Item {i}: {item.get('url', 'Unknown URL')}")
        elif len(content) < 100:
            issues['short_content'].append(f"Item {i}: {item.get('url', 'Unknown URL')} ({len(content)} chars)")
            
        # Check for duplicates
        if content:
            content_hash = hashlib.md5(content.encode()).hexdigest()
            if content_hash in content_hashes:
                issues['duplicate_content'].append(
                    f"Item {i} duplicates item {content_hashes[content_hash]}: {item.get('url', 'Unknown URL')}"
                )
            else:
                content_hashes[content_hash] = i
                
    return issues


def merge_scraped_data(data_files: List[str]) -> List[Dict]:
    """
    Merge multiple scraped data files
    
    Args:
        data_files: List of JSON file paths
        
    Returns:
        Merged data list
    """
    merged_data = []
    seen_urls = set()
    
    for filepath in data_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in data:
                url = item.get('url')
                if url and url not in seen_urls:
                    merged_data.append(item)
                    seen_urls.add(url)
                    
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            
    logger.info(f"Merged {len(merged_data)} unique pages from {len(data_files)} files")
    return merged_data