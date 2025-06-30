# CMU Health Services Web Scraper

A comprehensive web scraper designed to extract, process, and structure content from Carnegie Mellon University Health Services websites. This scraper is built with respect for rate limiting and follows best practices for ethical web scraping.

## Features

- **Intelligent Crawling**: Starts from the main UHS page and follows relevant links within the health services domain
- **Content Extraction**: Removes navigation elements, headers, and footers while preserving important content
- **URL Preservation**: Maintains source URLs for proper citation
- **Structured Output**: Saves content in multiple formats (JSON, CSV, Markdown)
- **Content Processing**: Cleans text, expands abbreviations, and extracts key information
- **Chunking for RAG**: Automatically chunks content for use in RAG (Retrieval-Augmented Generation) systems
- **Rate Limiting**: Respects server resources with configurable delays between requests
- **Validation**: Validates scraped data for completeness and quality

## Installation

1. Navigate to the scraper directory:
```bash
cd /Users/sivak/Development/jetbrains/CMU-UHS-RAG-CHATBOT/scraper
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Download required NLTK data:
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Usage

### Basic Usage

Run the scraper with default settings:
```bash
python run_scraper.py
```

### Advanced Options

```bash
# Scrape with custom delay between requests (2 seconds)
python run_scraper.py --delay 2.0

# Limit crawl depth to 3 levels
python run_scraper.py --max-depth 3

# Skip content processing for faster execution
python run_scraper.py --skip-processing

# Export to CSV and Markdown formats
python run_scraper.py --export-csv --export-markdown

# Use a different starting URL
python run_scraper.py --url "https://www.cmu.edu/health-services/services/"
```

### Command Line Arguments

- `--url`: Starting URL for scraping (default: CMU Health Services main page)
- `--delay`: Delay between requests in seconds (default: 1.0)
- `--max-depth`: Maximum crawl depth from the starting URL (default: 5)
- `--skip-processing`: Skip the content processing phase
- `--export-csv`: Export scraped data to CSV format
- `--export-markdown`: Export scraped data to Markdown files

## Output Structure

The scraper creates the following directory structure:

```
scraped_data/
├── raw/                 # Raw scraped data
│   └── cmu_health_raw_TIMESTAMP.json
├── processed/          # Processed and enhanced data
│   └── cmu_health_processed_TIMESTAMP.json
├── exports/            # Exported data in various formats
│   ├── cmu_health_TIMESTAMP.csv
│   ├── markdown_TIMESTAMP/
│   │   ├── INDEX.md
│   │   └── [page files].md
│   └── summary_TIMESTAMP.json
└── validation_report_TIMESTAMP.json
```

## Components

### 1. `cmu_health_scraper.py`
Main scraper class that handles:
- Web crawling with BFS (Breadth-First Search)
- URL filtering and validation
- Content extraction from HTML
- Respecting robots.txt
- Session management

### 2. `content_processor.py`
Processes scraped content:
- Text cleaning and normalization
- Abbreviation expansion
- Key information extraction (phone numbers, emails, addresses)
- Content chunking for RAG systems
- Q&A pair generation

### 3. `scraper_utils.py`
Utility functions for:
- Data validation
- Export to various formats
- URL hashing and deduplication
- Structured data extraction

### 4. `run_scraper.py`
Main orchestration script that:
- Coordinates the entire pipeline
- Handles command-line arguments
- Manages logging
- Generates reports

## Data Categories

The scraper automatically categorizes content into:
- **hours**: Operating hours and schedules
- **appointments**: Appointment information
- **services**: Available health services
- **insurance**: Insurance and billing information
- **counseling**: Mental health and counseling services
- **pharmacy**: Pharmacy services
- **health_education**: Health education resources
- **policies**: Policies and procedures
- **contact**: Contact information
- **about**: General information about UHS
- **general**: Other content

## Best Practices

1. **Rate Limiting**: The scraper includes a delay between requests. Adjust based on server capacity.
2. **Robots.txt**: The scraper respects robots.txt rules.
3. **Error Handling**: Failed URLs are logged and can be retried.
4. **Incremental Scraping**: Save data periodically to avoid data loss.

## Troubleshooting

### Common Issues

1. **Connection Errors**: Check internet connection and CMU website availability
2. **Rate Limiting**: Increase the delay between requests
3. **Missing Content**: Some pages may require JavaScript rendering (consider using Selenium)
4. **Memory Issues**: For large sites, consider reducing max_depth

### Logs

Check the log files for detailed information:
- `scraper.log`: General scraping logs
- `scraper_run_TIMESTAMP.log`: Specific run logs

## Integration with RAG Systems

The processed output is optimized for RAG systems:
- Content is chunked with configurable size and overlap
- Source URLs are preserved for citations
- Key information is extracted separately
- Clean, normalized text is provided

## Ethical Considerations

- This scraper is designed for educational and research purposes
- Always respect the website's terms of service
- Use appropriate delays to avoid overloading servers
- Consider reaching out to website administrators for large-scale scraping

## License

This scraper is part of the CMU-UHS-RAG-CHATBOT project and follows the project's licensing terms.

## Contributing

To contribute to this scraper:
1. Follow the existing code style
2. Add appropriate error handling
3. Update documentation for new features
4. Test thoroughly before submitting changes