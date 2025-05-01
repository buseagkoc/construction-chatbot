# Construction Chatbot

[![PyPI version](https://img.shields.io/badge/pypi-coming_soon-blue)](https://pypi.org/project/construction-chatbot/) [![CI](https://github.com/buseagkoc/construction-chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/buseagkoc/construction-chatbot/actions/workflows/ci.yml)
git add README.md


A lightweight RAG-powered chatbot built to query construction documents like specs, contracts, and legal PDFs using natural language. Whether you're using the command line or testing endpoints via Swagger UI, this bot’s got your back — context-aware answers.

Query construction documents using natural language. RAG, GPT-4, FastAPI, CLI.

---

## Quickstart

```bash
# 1. Clone & install
git clone https://github.com/buseagkoc/construction-chatbot.git
cd construction-chatbot
pip install -e .

# 2. Set up your environment
cp .env.example .env
# Open the .env file and paste your OpenAI API key

# 3. Try out the CLI
construction-chatbot chat "What’s a change order?"
# You'll get a fallback response if no documents are uploaded yet

# 4. Run the web API
construction-chatbot-api
# Then open http://localhost:8000/docs in your browser


## Features

-Ask questions using CLI or API
-Upload and parse PDFs into vector embeddings
-Get context-aware answers with citations
-Cache frequent queries with Redis
-Handles conversation memory
-CLI and FastAPI entrypoints — both install-and-run ready



## Tech Stack

-FastAPI – for web API
-Typer – for CLI interface
-ChromaDB – vector database
-OpenAI GPT-4 – language model
-Redis – for caching
-PyMuPDF – PDF parsing
-Pydantic + Dotenv – environment config

## Project Structure

construction-chatbot/
├── construction_chatbot/
│   ├── __main__.py
│   ├── webserver.py
│   ├── chatbot.py
│   ├── config.py
│   ├── document_processor.py
│   ├── pdf_handler.py
│   └── retriever.py
├── tests/
│   ├── test_chat.py
│   └── test_ingest.py
├── .env.example
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore

## Run Test
pytest
# All tests are mocked — no PDFs needed to validate logic

## CLI Usage Example
construction-chatbot chat "What’s the insulation spec for roofing?"

## API Usage Example

construction-chatbot-api
# Open http://localhost:8000/docs in your browser

## To Do

 Add .docx and .html support

 Document version tracking

 User authentication

 Publish to PyPI & Docker

 Add example PDF + notebook dem

#Contribution

git checkout -b feature/my-awesome-feature
# make your changes
pytest
black .
git commit -m "Add: my awesome feature"

## License
Free to use, remix, and build upon (note: this is POC & MPV level)