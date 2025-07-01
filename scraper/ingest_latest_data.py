#!/usr/bin/env python3
"""
Ingest latest CMU Health Services data into the RAG system
"""

import requests
import json
import os
from datetime import datetime

def ingest_latest_data():
    """Ingest the latest scraped data into the backend"""
    
    # Backend API endpoint
    api_url = "http://localhost:8080/api/v1/documents/upload"
    
    # Read the latest markdown file
    with open('scraped_latest/cmu_health_services_complete.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Also ingest the JSON data
    json_files = [f for f in os.listdir('scraped_latest') if f.endswith('.json') and f != 'summary.json']
    
    results = []
    
    # Upload the main markdown file
    print("Uploading main markdown file...")
    try:
        # Create a file-like object
        files = {
            'file': ('cmu_health_services_latest.md', content, 'text/markdown')
        }
        
        response = requests.post(api_url, files=files)
        
        if response.status_code == 200:
            print("✓ Successfully uploaded main markdown file")
            results.append({
                'file': 'cmu_health_services_latest.md',
                'status': 'success',
                'response': response.json()
            })
        else:
            print(f"✗ Failed to upload main markdown file: {response.status_code}")
            results.append({
                'file': 'cmu_health_services_latest.md',
                'status': 'failed',
                'error': response.text
            })
    except Exception as e:
        print(f"✗ Error uploading main markdown file: {str(e)}")
        results.append({
            'file': 'cmu_health_services_latest.md',
            'status': 'error',
            'error': str(e)
        })
    
    # Upload individual JSON files
    for json_file in json_files:
        print(f"Uploading {json_file}...")
        try:
            with open(f'scraped_latest/{json_file}', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert JSON to markdown format for better ingestion
            markdown_content = f"# {data.get('title', 'Untitled')}\n\n"
            markdown_content += f"*Source: {data.get('url', 'Unknown')}*\n\n"
            
            if data.get('meta_description'):
                markdown_content += f"{data['meta_description']}\n\n"
            
            # Add content
            for section in data.get('content', []):
                if section['type'] in ['h1', 'h2', 'h3', 'h4']:
                    level = '#' * (int(section['type'][1]) + 1)
                    markdown_content += f"{level} {section['text']}\n\n"
                else:
                    markdown_content += f"{section['text']}\n\n"
            
            # Upload as markdown
            files = {
                'file': (f"{data['id']}.md", markdown_content, 'text/markdown')
            }
            
            response = requests.post(api_url, files=files)
            
            if response.status_code == 200:
                print(f"  ✓ Successfully uploaded {json_file}")
                results.append({
                    'file': json_file,
                    'status': 'success'
                })
            else:
                print(f"  ✗ Failed to upload {json_file}: {response.status_code}")
                results.append({
                    'file': json_file,
                    'status': 'failed',
                    'error': response.text
                })
                
        except Exception as e:
            print(f"  ✗ Error processing {json_file}: {str(e)}")
            results.append({
                'file': json_file,
                'status': 'error',
                'error': str(e)
            })
    
    # Summary
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] in ['failed', 'error'])
    
    print(f"\n=== Ingestion Summary ===")
    print(f"Total files: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    # Save results
    with open('scraped_latest/ingestion_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': len(results),
                'successful': successful,
                'failed': failed
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nResults saved to scraped_latest/ingestion_results.json")
    
    # Also use the batch endpoint for comprehensive ingestion
    print("\nIngesting via batch endpoint...")
    try:
        batch_data = {
            'path': 'scraped_latest'
        }
        response = requests.post(
            "http://localhost:8080/api/v2/ingest/scraped-data",
            json=batch_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✓ Batch ingestion successful")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"✗ Batch ingestion failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error in batch ingestion: {str(e)}")


if __name__ == "__main__":
    ingest_latest_data()