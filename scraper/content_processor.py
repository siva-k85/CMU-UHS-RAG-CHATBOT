#!/usr/bin/env python3
"""
Content processor for CMU Health Services scraped data

This module provides utilities for processing, cleaning, and enriching
the scraped content for better use in RAG systems.
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import logging

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

logger = logging.getLogger(__name__)

class ContentProcessor:
    """Process and enhance scraped content"""
    
    def __init__(self):
        """Initialize the content processor"""
        self.stop_words = set(stopwords.words('english'))
        
        # Common health-related abbreviations to expand
        self.abbreviations = {
            'UHS': 'University Health Services',
            'CMU': 'Carnegie Mellon University',
            'CAPS': 'Counseling and Psychological Services',
            'COVID': 'Coronavirus Disease',
            'FAQ': 'Frequently Asked Questions',
            'ID': 'Identification',
            'Dr.': 'Doctor',
            'PA': 'Physician Assistant',
            'NP': 'Nurse Practitioner',
            'RN': 'Registered Nurse',
            'MD': 'Medical Doctor',
            'PhD': 'Doctor of Philosophy',
            'Mon': 'Monday',
            'Tue': 'Tuesday',
            'Wed': 'Wednesday',
            'Thu': 'Thursday',
            'Fri': 'Friday',
            'Sat': 'Saturday',
            'Sun': 'Sunday'
        }
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\'\"\/]', ' ', text)
        
        # Fix common encoding issues
        text = text.replace('\u2019', "'")
        text = text.replace('\u2018', "'")
        text = text.replace('\u201c', '"')
        text = text.replace('\u201d', '"')
        text = text.replace('\u2013', '-')
        text = text.replace('\u2014', '--')
        
        # Remove multiple consecutive punctuation
        text = re.sub(r'([.!?])\1+', r'\1', text)
        
        # Ensure space after punctuation
        text = re.sub(r'([.!?,;:])([A-Za-z])', r'\1 \2', text)
        
        return text.strip()
        
    def expand_abbreviations(self, text: str) -> str:
        """
        Expand common abbreviations
        
        Args:
            text: Text with abbreviations
            
        Returns:
            Text with expanded abbreviations
        """
        for abbr, full in self.abbreviations.items():
            # Match whole words only
            pattern = r'\b' + re.escape(abbr) + r'\b'
            text = re.sub(pattern, full, text, flags=re.IGNORECASE)
        return text
        
    def extract_key_information(self, content: Dict) -> Dict:
        """
        Extract key information from content
        
        Args:
            content: Page content dictionary
            
        Returns:
            Dictionary with extracted key information
        """
        text = content.get('content', '')
        
        # Extract phone numbers
        phone_pattern = r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
        phones = re.findall(phone_pattern, text)
        
        # Extract email addresses
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        emails = re.findall(email_pattern, text)
        
        # Extract hours/times
        time_pattern = r'(\d{1,2}:\d{2}\s*[APap][Mm])'
        times = re.findall(time_pattern, text)
        
        # Extract addresses
        address_pattern = r'(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd)[,.\s]+(?:Suite|Ste|Room|Rm)?\s*\d*)'
        addresses = re.findall(address_pattern, text)
        
        # Extract important keywords
        health_keywords = self._extract_health_keywords(text)
        
        return {
            'phone_numbers': list(set(phones)),
            'email_addresses': list(set(emails)),
            'times_mentioned': list(set(times)),
            'addresses': list(set(addresses)),
            'health_keywords': health_keywords
        }
        
    def _extract_health_keywords(self, text: str) -> List[str]:
        """Extract health-related keywords"""
        health_terms = [
            'appointment', 'vaccine', 'vaccination', 'immunization',
            'insurance', 'copay', 'deductible', 'prescription',
            'medication', 'pharmacy', 'counseling', 'therapy',
            'mental health', 'wellness', 'prevention', 'screening',
            'emergency', 'urgent care', 'primary care', 'specialist',
            'referral', 'consultation', 'diagnosis', 'treatment',
            'symptom', 'condition', 'allergy', 'chronic',
            'acute', 'health record', 'medical history', 'lab',
            'test', 'result', 'x-ray', 'blood work'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for term in health_terms:
            if term in text_lower:
                found_keywords.append(term)
                
        return found_keywords
        
    def create_chunks(self, text: str, chunk_size: int = 500, 
                     overlap: int = 50) -> List[Dict]:
        """
        Create overlapping text chunks for RAG
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in words
            overlap: Number of words to overlap
            
        Returns:
            List of chunk dictionaries
        """
        # Tokenize into sentences
        sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            words = word_tokenize(sentence)
            word_count = len(words)
            
            if current_size + word_count > chunk_size and current_chunk:
                # Create chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'word_count': current_size,
                    'sentence_count': len(current_chunk)
                })
                
                # Keep overlap
                if overlap > 0:
                    overlap_sentences = []
                    overlap_size = 0
                    
                    for sent in reversed(current_chunk):
                        sent_words = len(word_tokenize(sent))
                        if overlap_size + sent_words <= overlap:
                            overlap_sentences.insert(0, sent)
                            overlap_size += sent_words
                        else:
                            break
                            
                    current_chunk = overlap_sentences
                    current_size = overlap_size
                else:
                    current_chunk = []
                    current_size = 0
                    
            current_chunk.append(sentence)
            current_size += word_count
            
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'word_count': current_size,
                'sentence_count': len(current_chunk)
            })
            
        return chunks
        
    def process_scraped_data(self, scraped_data: List[Dict]) -> List[Dict]:
        """
        Process all scraped data
        
        Args:
            scraped_data: List of scraped page data
            
        Returns:
            List of processed page data
        """
        processed_data = []
        
        for page_data in scraped_data:
            try:
                # Clean content
                cleaned_content = self.clean_text(page_data.get('content', ''))
                expanded_content = self.expand_abbreviations(cleaned_content)
                
                # Extract key information
                key_info = self.extract_key_information({
                    'content': expanded_content
                })
                
                # Create chunks for RAG
                chunks = self.create_chunks(expanded_content)
                
                # Create processed entry
                processed_entry = {
                    'url': page_data['url'],
                    'title': self.clean_text(page_data.get('title', '')),
                    'category': page_data.get('category', 'general'),
                    'original_content': page_data.get('content', ''),
                    'cleaned_content': expanded_content,
                    'chunks': chunks,
                    'key_information': key_info,
                    'metadata': {
                        'scraped_at': page_data.get('scraped_at'),
                        'processed_at': datetime.now().isoformat(),
                        'content_length': len(expanded_content),
                        'chunk_count': len(chunks)
                    }
                }
                
                processed_data.append(processed_entry)
                
            except Exception as e:
                logger.error(f"Error processing page {page_data.get('url')}: {e}")
                continue
                
        return processed_data
        
    def create_qa_pairs(self, content: str, title: str) -> List[Dict]:
        """
        Generate potential Q&A pairs from content
        
        Args:
            content: Page content
            title: Page title
            
        Returns:
            List of Q&A pairs
        """
        qa_pairs = []
        
        # Look for FAQ patterns
        faq_pattern = r'(?:Q:|Question:)\s*(.+?)(?:\n|$)(?:A:|Answer:)\s*(.+?)(?=(?:Q:|Question:|$))'
        faqs = re.findall(faq_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for question, answer in faqs:
            qa_pairs.append({
                'question': self.clean_text(question),
                'answer': self.clean_text(answer),
                'type': 'explicit_faq'
            })
            
        # Generate questions from headings
        heading_pattern = r'(?:^|\n)#+\s*(.+?)(?:\n|$)'
        headings = re.findall(heading_pattern, content)
        
        for heading in headings:
            heading_clean = self.clean_text(heading)
            if len(heading_clean) > 10:  # Skip short headings
                # Find content after this heading
                heading_pos = content.find(heading)
                if heading_pos != -1:
                    # Get content until next heading or end
                    next_heading = re.search(r'\n#+\s', content[heading_pos + len(heading):])
                    if next_heading:
                        answer_text = content[heading_pos:heading_pos + next_heading.start()]
                    else:
                        answer_text = content[heading_pos:heading_pos + 500]  # Limit length
                        
                    qa_pairs.append({
                        'question': f"What is {heading_clean}?",
                        'answer': self.clean_text(answer_text),
                        'type': 'heading_based'
                    })
                    
        return qa_pairs


def main():
    """Example usage of content processor"""
    # Load scraped data
    with open('scraped_data/cmu_health_services.json', 'r') as f:
        scraped_data = json.load(f)
        
    # Process data
    processor = ContentProcessor()
    processed_data = processor.process_scraped_data(scraped_data)
    
    # Save processed data
    with open('scraped_data/processed_content.json', 'w') as f:
        json.dump(processed_data, f, indent=2)
        
    logger.info(f"Processed {len(processed_data)} pages")


if __name__ == "__main__":
    main()