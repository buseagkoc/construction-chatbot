from app.document_processor import DocumentProcessor
from pathlib import Path

def test_document_processing():
    # Initialize processor
    processor = DocumentProcessor()
    
    try:
        # Process a test document
        doc_id = 'test_doc'
        # Replace with path to your test PDF
        doc_path = Path('data/documents/test.pdf')  
        
        result = processor.process_document(str(doc_path), doc_id)
        
        # Print results
        print(f"\nProcessed document {doc_id}:")
        print(f"Total pages: {result['total_pages']}")
        print(f"Number of sections: {len(result['sections'])}")
        
        # Print first section as sample
        if result['sections']:
            first_section = result['sections'][0]
            print("\nFirst section sample:")
            print(f"Title: {first_section['title']}")
            print(f"Page: {first_section['page']}")
            print(f"Content preview: {first_section['content'][:200]}...")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == '__main__':
    test_document_processing()
