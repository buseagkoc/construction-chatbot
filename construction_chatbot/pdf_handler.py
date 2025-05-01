from typing import Union, List, Dict
import fitz
from pathlib import Path
import re
from datetime import datetime

class FitzPDFHandler:  
    """Handles PDF documents for construction document chatbot."""

    def __init__(self, input_source: Union[Path, str, bytes]):
        """
        Initialize PDF handler with multiple input source types.
        
        Args:
            input_source: Can be a Path object, string path, or bytes of PDF content
        """
        if isinstance(input_source, Path):
            self.document = self._load_from_path(input_source)
        elif isinstance(input_source, bytes):
            self.document = self._load_from_bytes(input_source)
        elif isinstance(input_source, str):
            self.document = self._load_from_path(Path(input_source))
        else:
            raise ValueError("Input source must be a Path, string path, or bytes.")

    def _load_from_path(self, input_source: Path) -> fitz.Document:
        """Load PDF from file path."""
        try:
            return fitz.open(input_source)
        except Exception as e:
            raise ValueError(f"Error loading PDF from path: {str(e)}")

    def _load_from_bytes(self, input_source: bytes) -> fitz.Document:
        """Load PDF from bytes."""
        try:
            return fitz.open(stream=input_source)
        except Exception as e:
            raise ValueError(f"Error loading PDF from bytes: {str(e)}")

    @property
    def number_of_pages(self) -> int:
        """Get the number of pages in the document."""
        return len(self.document)

    def get_page_text(self, page_number: int) -> str:
        """
        Extract text content from a specific page.

        Args:
            page_number (int): Page number (1-based indexing)
        Returns:
            str: Text content of the page
        """
        try:
            return self.document[page_number - 1].get_text()
        except IndexError:
            raise ValueError(f"Page number {page_number} out of range")
        except Exception as e:
            raise Exception(f"Error extracting text from page {page_number}: {str(e)}")

    def get_document_text(self) -> str:
        """Extract text from entire document."""
        try:
            return "\n".join(
                self.get_page_text(page_num)
                for page_num in range(1, self.number_of_pages + 1)
            )
        except Exception as e:
            raise Exception(f"Error extracting document text: {str(e)}")

    def extract_section_text(self, start_page: int, end_page: int) -> str:
        """
        Extract text from a range of pages.

        Args:
            start_page (int): Starting page number (1-based)
            end_page (int): Ending page number (1-based)
        Returns:
            str: Combined text from the page range
        """
        if start_page < 1 or end_page > self.number_of_pages or start_page > end_page:
            raise ValueError("Invalid page range")
            
        return "\n".join(
            self.get_page_text(page_num)
            for page_num in range(start_page, end_page + 1)
        )

    def get_metadata(self) -> Dict:
        """Extract document metadata relevant to construction documents."""
        try:
            first_page_text = self.get_page_text(1)
            
            return {
                'title': self.document.metadata.get('title', ''),
                'document_type': self._identify_document_type(first_page_text),
                'document_date': self._extract_date(first_page_text),
                'project_number': self._extract_project_number(first_page_text),
                'page_count': self.number_of_pages,
                'revision_number': self._extract_revision_number(first_page_text)
            }
        except Exception as e:
            raise Exception(f"Error extracting metadata: {str(e)}")

    def _identify_document_type(self, text: str) -> str:
        """Identify the type of construction document."""
        document_types = {
            'contract': ['agreement', 'contract', 'general conditions'],
            'specifications': ['technical specifications', 'specifications', 'spec'],
            'drawing': ['drawing', 'plan', 'detail'],
            'permit': ['permit', 'certification', 'approval'],
            'submittal': ['submittal', 'shop drawing', 'material data'],
            'estimate': ['estimate', 'budget', 'cost analysis'],
            'schedule': ['schedule', 'timeline', 'project timeline'],
            'inspection': ['inspection report', 'site inspection', 'field report'],
            'change_order': ['change order', 'work change directive', 'modification']
        }

        text_lower = text.lower()
        for doc_type, keywords in document_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return doc_type
        return 'unspecified'

    def _extract_date(self, text: str) -> str:
        """Extract date from document text."""
        date_patterns = [
            r'Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'Issued:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'Rev\s*Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s*(?:Rev|Issue|Date)',
            r'Effective\s*Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return ''

    def _extract_project_number(self, text: str) -> str:
        """Extract project number if present."""
        project_patterns = [
            r'Project\s*(?:No|Number|#)[:.]?\s*([A-Za-z0-9-]+)',
            r'Project\s*ID[:.]?\s*([A-Za-z0-9-]+)',
            r'Contract\s*(?:No|Number|#)[:.]?\s*([A-Za-z0-9-]+)',
            r'Job\s*(?:No|Number|#)[:.]?\s*([A-Za-z0-9-]+)'
        ]

        for pattern in project_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return ''

    def _extract_revision_number(self, text: str) -> str:
        """Extract revision number if present."""
        revision_patterns = [
            r'Rev(?:ision)?\s*(?:No|Number|#)?[:.]?\s*([A-Za-z0-9-]+)',
            r'Version\s*[:.]?\s*([A-Za-z0-9-]+)',
            r'Update\s*[:.]?\s*([A-Za-z0-9-]+)',
            r'(?:Rev|Revision)\s*([A-Za-z0-9-]+)'
        ]

        for pattern in revision_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return ''

    def extract_table_of_contents(self) -> List[Dict]:
        """
        Attempt to extract table of contents or section headers.
        Returns list of {'title': str, 'page': int} dictionaries.
        """
        toc = []
        try:
            # Try to get PDF's built-in TOC
            pdf_toc = self.document.get_toc()
            if pdf_toc:
                return [{'title': title, 'page': page} for _, page, title, _ in pdf_toc]
            
            # If no built-in TOC, try to parse first few pages
            first_pages_text = self.extract_section_text(1, min(5, self.number_of_pages))
            
            # Look for common section patterns
            section_patterns = [
                r'^(?:Section|SECTION)\s+(\d+\.?\d*)\s+([^\n]+)',
                r'^(\d+\.?\d*)\s+([A-Z][^\n]+)',
                r'^(?:ARTICLE|Article)\s+(\d+)\s+([^\n]+)'
            ]
            
            for pattern in section_patterns:
                matches = re.finditer(pattern, first_pages_text, re.MULTILINE)
                for match in matches:
                    toc.append({
                        'title': f"{match.group(1)} {match.group(2).strip()}",
                        'page': None  # We don't know the page number
                    })
                    
            return toc
            
        except Exception as e:
            print(f"Warning: Could not extract table of contents: {str(e)}")
            return []

    def close(self):
        """Close the PDF document."""
        try:
            self.document.close()
        except Exception as e:
            print(f"Warning: Error closing document: {str(e)}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()