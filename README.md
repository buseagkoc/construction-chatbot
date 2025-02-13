# Construction Document Chatbot

A RAG-based chatbot for querying construction documents and Florida construction law. Built with FastAPI and OpenAI, this system allows efficient document processing and intelligent querying of construction specifications and regulations.

## Features

- Process and analyze construction PDFs
- Extract structured sections from documents
- Query documents using natural language
- Get context-aware responses with source citations
- Batch processing for efficient document handling

## Tech Stack

- FastAPI for API endpoints
- ChromaDB for vector storage
- OpenAI GPT-4 for response generation
- Redis for response caching
- PyMuPDF for PDF processing

## Project Structure

```
construction-chatbot/
├── app/
│   ├── __init__.py
│   ├── document_processor.py  # PDF section extraction
│   ├── pdf_handler.py        # PDF file operations
│   ├── retriever.py         # Vector storage & RAG
│   └── chatbot.py          # Core chatbot logic
├── data/
│   └── documents/          # Document storage
├── main.py                 # FastAPI application
└── requirements.txt        # Dependencies
```

## Setup

1. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Add your OpenAI API key to .env
```

3. Start Redis:
```bash
redis-server
```

4. Run the application:
```bash
python main.py
```

## API Usage

### Upload Document
```bash
curl -X POST -F "file=@example.pdf" http://localhost:8000/documents/upload
```

### Query Document
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the concrete specifications?"}' \
  http://localhost:8000/chat
```

## Development Notes

- Handles both small and large documents efficiently
- Processes documents in batches to optimize throughput
- Implements caching to reduce redundant API calls
- Uses conversation history for context-aware responses

## Todo

- [ ] Add user authentication
- [ ] Implement document version tracking
- [ ] Add more Florida construction law context
- [ ] Enhance section extraction for complex documents