from typing import Dict, List
from app.pdf_handler import FitzPDFHandler  
import re

class DocumentProcessor:
    def __init__(self):
        self.documents = {}

    def process_document(self, file_path: str, doc_id: str) -> Dict:
        """Process a construction document and extract its contents"""
        try:
            # Initialize the PDF handler
            pdf_handler = FitzPDFHandler(file_path)
            
            # Extract document sections
            sections = []
            
            # Process each page
            for page_num in range(1, pdf_handler.number_of_pages + 1):
                text = pdf_handler.get_page_text(page_num)
                
                # Split into sections based on headers
                page_sections = self._split_into_sections(text, page_num)
                sections.extend(page_sections)
            
            # Store processed document
            self.documents[doc_id] = {
                'sections': sections,
                'total_pages': pdf_handler.number_of_pages
            }
            
            # Clean up
            pdf_handler.close()
            
            return self.documents[doc_id]
            
        except Exception as e:
            raise Exception(f"Error processing document {doc_id}: {str(e)}")
    
    def _split_into_sections(self, text: str, page_num: int) -> List[Dict]:
        """Split text into logical sections"""
        sections = []
        current_section = {
            'title': '',
            'content': '',
            'page': page_num
        }
        
        # Split text into lines
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a header
            if self._is_section_header(line):
                # Save previous section if it exists
                if current_section['content']:
                    sections.append(current_section)
                    
                # Start new section
                current_section = {
                    'title': line,
                    'content': '',
                    'page': page_num
                }
            else:
                current_section['content'] += line + '\n'
        
        # Add final section
        if current_section['content']:
            sections.append(current_section)
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """Check if line is likely a section header"""
        header_patterns = [
            r'^\d+\.\d+\s+[A-Z]',  # Matches patterns like "1.1 GENERAL"
            r'^SECTION\s+\d{2}',    # Matches "SECTION 01"
            r'^Article\s+\d+',      # Matches "Article 1"
            r'^\d+\.\s+[A-Z]',      # Matches "1. SCOPE"
        ]
        
        return any(re.match(pattern, line) for pattern in header_patterns)

    def search_documents(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search through processed documents for relevant sections"""
        results = []
        
        # Convert query to lowercase for case-insensitive matching
        query = query.lower()
        
        # Search through all documents
        for doc_id, doc in self.documents.items():
            for section in doc['sections']:
                if (query in section['title'].lower() or 
                    query in section['content'].lower()):
                    results.append({
                        'doc_id': doc_id,
                        'title': section['title'],
                        'content': section['content'],
                        'page': section['page']
                    })
        
        # Sort by relevance (simple contains check)
        results.sort(key=lambda x: 
            x['title'].lower().count(query) + 
            x['content'].lower().count(query), 
            reverse=True)
        
        return results[:max_results]