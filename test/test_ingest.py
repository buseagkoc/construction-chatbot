import os
os.environ.setdefault("OPENAI_API_KEY", "test_key")

import pytest
import asyncio
from pathlib import Path
from construction_chatbot.chatbot import ConstructionChatbot

@pytest.mark.asyncio
async def test_process_document_fallback(monkeypatch, tmp_path):
    # Prepare dummy PDF
    dummy = tmp_path / "dummy.pdf"
    dummy.write_bytes(b"%PDF-1.4\n%%EOF")

    fake_sections = [{"title": "HEAD", "content": "BODY", "page": 1}]
    monkeypatch.setattr(
        "construction_chatbot.document_processor.DocumentProcessor.process_document",
        lambda self, path, doc_id: {"sections": fake_sections}
    )
    monkeypatch.setattr(
        "construction_chatbot.retriever.DocumentRetriever.add_sections",
        lambda self, doc_id, sections: None
    )

    bot = ConstructionChatbot()
    result = await bot.process_document(dummy)
    assert result["status"] == "success"
    assert result["sections_processed"] == len(fake_sections)
    assert result["doc_id"].startswith("doc_dummy")
