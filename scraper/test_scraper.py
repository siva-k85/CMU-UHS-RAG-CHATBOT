#!/usr/bin/env python3
"""
Test script for CMU Health Services scraper

This script runs basic tests to ensure the scraper components work correctly.
"""

import json
import logging
from datetime import datetime

from cmu_health_scraper import CMUHealthScraper
from content_processor import ContentProcessor
from scraper_utils import ScraperUtils, DataExporter, validate_scraped_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_scraping():
    """Test basic scraping functionality"""
    logger.info("Testing basic scraping functionality...")
    
    # Create scraper with limited scope for testing
    scraper = CMUHealthScraper(
        base_url="https://www.cmu.edu/health-services/",
        delay=1.0,
        max_depth=1  # Only scrape 1 level deep for testing
    )
    
    # Test single page scraping
    test_url = "https://www.cmu.edu/health-services/"
    page_data = scraper.scrape_page(test_url)
    
    if page_data:
        logger.info("✓ Successfully scraped test page")
        logger.info(f"  Title: {page_data['title']}")
        logger.info(f"  Content length: {len(page_data['content'])} characters")
        logger.info(f"  Category: {page_data['category']}")
        return True
    else:
        logger.error("✗ Failed to scrape test page")
        return False


def test_content_processing():
    """Test content processing functionality"""
    logger.info("\nTesting content processing...")
    
    # Create test content
    test_content = [{
        'url': 'https://example.com/test',
        'title': 'Test Page - UHS Hours',
        'content': '''
        Welcome to UHS! Our hours are Mon-Fri 8:30 AM - 5:00 PM.
        Call us at 412-268-2157 or email health@cmu.edu.
        We are located at 1060 Morewood Avenue, Pittsburgh, PA 15213.
        ''',
        'category': 'hours',
        'scraped_at': datetime.now().isoformat()
    }]
    
    processor = ContentProcessor()
    processed = processor.process_scraped_data(test_content)
    
    if processed and len(processed) > 0:
        logger.info("✓ Successfully processed content")
        
        # Check key information extraction
        key_info = processed[0]['key_information']
        logger.info(f"  Phone numbers found: {key_info['phone_numbers']}")
        logger.info(f"  Email addresses found: {key_info['email_addresses']}")
        logger.info(f"  Times found: {key_info['times_mentioned']}")
        
        # Check chunking
        chunks = processed[0]['chunks']
        logger.info(f"  Created {len(chunks)} chunks")
        
        return True
    else:
        logger.error("✗ Failed to process content")
        return False


def test_utils():
    """Test utility functions"""
    logger.info("\nTesting utility functions...")
    
    # Test URL utilities
    test_url = "https://www.cmu.edu/health-services/index.html"
    url_hash = ScraperUtils.create_url_hash(test_url)
    domain_info = ScraperUtils.extract_domain_info(test_url)
    
    logger.info(f"✓ URL hash: {url_hash}")
    logger.info(f"✓ Domain: {domain_info['domain']}")
    
    # Test text normalization
    test_text = "This   is\t\ta    test\n\n\n\nwith weird     spacing"
    normalized = ScraperUtils.normalize_whitespace(test_text)
    logger.info(f"✓ Normalized text: '{normalized}'")
    
    return True


def test_validation():
    """Test data validation"""
    logger.info("\nTesting data validation...")
    
    # Create test data with some issues
    test_data = [
        {
            'url': 'https://example.com/1',
            'title': 'Good Page',
            'content': 'This is a good page with sufficient content. ' * 20
        },
        {
            'url': 'https://example.com/2',
            'title': '',  # Missing title
            'content': 'Content without title'
        },
        {
            'url': 'https://example.com/3',
            'title': 'Short Content',
            'content': 'Too short'  # Short content
        },
        {
            'url': '',  # Missing URL
            'title': 'No URL',
            'content': 'Content without URL'
        }
    ]
    
    issues = validate_scraped_data(test_data)
    
    logger.info("✓ Validation completed")
    for issue_type, issue_list in issues.items():
        if issue_list:
            logger.info(f"  {issue_type}: {len(issue_list)} issues")
            
    return True


def test_export():
    """Test data export functionality"""
    logger.info("\nTesting data export...")
    
    # Create test data
    test_data = [{
        'url': 'https://www.cmu.edu/health-services/test',
        'title': 'Test Export Page',
        'content': 'This is test content for export functionality.',
        'category': 'test',
        'scraped_at': datetime.now().isoformat()
    }]
    
    exporter = DataExporter()
    
    # Test CSV export
    try:
        exporter.export_to_csv(test_data, 'test_export.csv')
        logger.info("✓ CSV export successful")
    except Exception as e:
        logger.error(f"✗ CSV export failed: {e}")
        
    # Test summary report
    try:
        exporter.create_summary_report(test_data, 'test_summary.json')
        logger.info("✓ Summary report created")
    except Exception as e:
        logger.error(f"✗ Summary report failed: {e}")
        
    return True


def main():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("CMU Health Services Scraper Test Suite")
    logger.info("=" * 50)
    
    tests = [
        ("Basic Scraping", test_basic_scraping),
        ("Content Processing", test_content_processing),
        ("Utilities", test_utils),
        ("Validation", test_validation),
        ("Export", test_export)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
            
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("Test Summary")
    logger.info("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
        
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    # Cleanup test files
    import os
    for file in ['test_export.csv', 'test_summary.json']:
        if os.path.exists(file):
            os.remove(file)
            

if __name__ == "__main__":
    main()