#!/usr/bin/env python3
"""
Main runner script for CMU Health Services web scraper

This script orchestrates the entire scraping, processing, and export pipeline.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
import json

from cmu_health_scraper import CMUHealthScraper
from content_processor import ContentProcessor
from scraper_utils import DataExporter, validate_scraped_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'scraper_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup_directories():
    """Create necessary directories"""
    directories = [
        'scraped_data',
        'scraped_data/raw',
        'scraped_data/processed',
        'scraped_data/exports',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")


def run_scraping_pipeline(args):
    """
    Run the complete scraping pipeline
    
    Args:
        args: Command line arguments
    """
    logger.info("Starting CMU Health Services scraping pipeline")
    
    # Setup directories
    setup_directories()
    
    # Phase 1: Scraping
    logger.info("Phase 1: Web Scraping")
    scraper = CMUHealthScraper(
        base_url=args.url,
        delay=args.delay,
        max_depth=args.max_depth
    )
    
    # Run the scraper
    scraper.crawl()
    
    # Save raw scraped data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_data_path = f"scraped_data/raw/cmu_health_raw_{timestamp}.json"
    
    with open(raw_data_path, 'w', encoding='utf-8') as f:
        json.dump(scraper.scraped_content, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved raw data to {raw_data_path}")
    
    # Phase 2: Content Processing
    if not args.skip_processing:
        logger.info("Phase 2: Content Processing")
        processor = ContentProcessor()
        processed_data = processor.process_scraped_data(scraper.scraped_content)
        
        # Save processed data
        processed_data_path = f"scraped_data/processed/cmu_health_processed_{timestamp}.json"
        with open(processed_data_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved processed data to {processed_data_path}")
        
        # Use processed data for export
        export_data = processed_data
    else:
        export_data = scraper.scraped_content
        
    # Phase 3: Validation
    logger.info("Phase 3: Data Validation")
    validation_issues = validate_scraped_data(export_data)
    
    # Log validation results
    for issue_type, issues in validation_issues.items():
        if issues:
            logger.warning(f"{issue_type}: {len(issues)} issues found")
            for issue in issues[:5]:  # Show first 5 issues
                logger.warning(f"  - {issue}")
                
    # Save validation report
    validation_path = f"scraped_data/validation_report_{timestamp}.json"
    with open(validation_path, 'w', encoding='utf-8') as f:
        json.dump(validation_issues, f, indent=2)
        
    # Phase 4: Export
    logger.info("Phase 4: Data Export")
    exporter = DataExporter()
    
    # Export to various formats
    if args.export_csv:
        csv_path = f"scraped_data/exports/cmu_health_{timestamp}.csv"
        exporter.export_to_csv(export_data, csv_path)
        
    if args.export_markdown:
        md_dir = f"scraped_data/exports/markdown_{timestamp}"
        exporter.export_to_markdown(export_data, md_dir)
        
    # Always create summary report
    summary_path = f"scraped_data/exports/summary_{timestamp}.json"
    exporter.create_summary_report(export_data, summary_path)
    
    # Final statistics
    logger.info("=" * 50)
    logger.info("Scraping Pipeline Complete!")
    logger.info(f"Total pages scraped: {len(scraper.scraped_content)}")
    logger.info(f"Failed URLs: {len(scraper.failed_urls)}")
    if scraper.failed_urls:
        for url in list(scraper.failed_urls)[:5]:
            logger.info(f"  - {url}")
    logger.info("=" * 50)
    
    return {
        'success': True,
        'pages_scraped': len(scraper.scraped_content),
        'failed_urls': len(scraper.failed_urls),
        'timestamp': timestamp
    }


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='CMU Health Services Web Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scraping with default settings
  python run_scraper.py
  
  # Scrape with custom delay and depth
  python run_scraper.py --delay 2.0 --max-depth 3
  
  # Skip content processing for faster execution
  python run_scraper.py --skip-processing
  
  # Export to all formats
  python run_scraper.py --export-csv --export-markdown
        """
    )
    
    parser.add_argument(
        '--url',
        default='https://www.cmu.edu/health-services/',
        help='Starting URL for scraping (default: CMU Health Services main page)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=5,
        help='Maximum crawl depth (default: 5)'
    )
    
    parser.add_argument(
        '--skip-processing',
        action='store_true',
        help='Skip content processing phase'
    )
    
    parser.add_argument(
        '--export-csv',
        action='store_true',
        help='Export data to CSV format'
    )
    
    parser.add_argument(
        '--export-markdown',
        action='store_true',
        help='Export data to Markdown format'
    )
    
    args = parser.parse_args()
    
    try:
        result = run_scraping_pipeline(args)
        sys.exit(0 if result['success'] else 1)
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()