# CMU Health Services Web Scraping Results

## Summary

The enhanced web scraper has been created with the following capabilities:

### Features Implemented

1. **Comprehensive Web Scraping**
   - Crawls all CMU Health Services websites
   - Follows links up to 3 levels deep
   - Respects domain boundaries

2. **PDF Extraction**
   - Downloads all PDF documents
   - Extracts text using both PyPDF2 and pdfplumber
   - Preserves tables and metadata
   - Special handling for insurance-related PDFs

3. **XML Export Format**
   - Structured XML for each scraped page
   - Separate sections for HTML and PDF content
   - Metadata preservation including URLs and timestamps

4. **Insurance Content Detection**
   - Identifies insurance-related pages and documents
   - Stores in separate `insurance/` directory
   - Keywords: insurance, coverage, benefits, claim, copay, deductible, etc.

### Directory Structure Created

```
scraped_data_xml/
├── pages/          # General HTML pages
├── insurance/      # Insurance-specific content
├── pdfs/           # Downloaded PDF files
└── summary.json    # Scraping statistics
```

### Target URLs

The scraper targets these CMU Health Services domains:
- https://www.cmu.edu/health-services/
- https://www.cmu.edu/health-services/student-insurance/
- https://www.cmu.edu/health-services/billing-insurance/
- https://www.cmu.edu/counseling/
- https://www.cmu.edu/wellness/

### Usage Instructions

1. **Run the scraper**:
   ```bash
   cd scraper
   python run_enhanced_scraper.py
   ```

2. **Convert to RAG format**:
   ```bash
   python xml_to_rag_ingester.py
   ```

### Expected Output

When the scraper completes, you'll have:

1. **XML Files**: Each page/PDF converted to structured XML
2. **PDF Downloads**: All PDFs preserved in original format
3. **Summary Report**: Statistics on pages scraped, PDFs found, etc.
4. **RAG-Ready JSON**: Formatted data ready for vector embedding

### Key Benefits

- **Comprehensive Coverage**: Gets all health services information
- **Insurance Focus**: Special attention to insurance documents
- **Structured Data**: XML format preserves hierarchy and metadata
- **Citation Support**: URLs and sources preserved for RAG citations
- **Table Extraction**: Complex PDF tables converted to structured format

The scraper is currently running and will extract all available information from the CMU Health Services websites.