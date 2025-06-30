#!/usr/bin/env python3
"""
Run the enhanced CMU Health Services scraper
This script installs dependencies and runs the scraper
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed successfully!")

def main():
    # Change to scraper directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Install dependencies
    try:
        install_dependencies()
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        print("Please install manually: pip install -r requirements.txt")
        return
    
    # Run the enhanced scraper
    print("\n" + "="*50)
    print("Starting Enhanced CMU Health Services Scraper")
    print("This will scrape all pages and PDFs, especially insurance-related content")
    print("Output will be saved in XML format in 'scraped_data_xml' directory")
    print("="*50 + "\n")
    
    try:
        subprocess.run([sys.executable, "enhanced_cmu_scraper.py"])
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error running scraper: {e}")

if __name__ == "__main__":
    main()