import pytest
import asyncio
from pathlib import Path
from construction_chatbot.chatbot import ConstructionChatbot

@pytest.mark.asyncio
async def test_process_document_fallback(monkeypatch, tmp_path):
    # 1) Create a tiny “dummy.pdf” (not a real PDF, just any bytes)
    dummy = tmp_path / "dummy.pdf"
    dummy.write_bytes(b"%PDF-1.4\n%%EOF")

    # 2) Monkey-patch the DocumentProcessor to return a known result
    fake_sections = [{"title":"HEAD","content":"BODY","page":1}]
    async def fake_add_sections(self, doc_id, sections):
        return None
    monkeypatch.setattr(
        "construction_chatbot.document_processor.DocumentProcessor.process_document",
        lambda self, path, doc_id: {"sections": fake_sections}
    )
    monkeypatch.setattr(
        "construction_chatbot.retriever.DocumentRetriever.add_sections",
        fake_add_sections
    )

    # 3) Run your method
    bot = ConstructionChatbot()
    result = await bot.process_document(dummy)

    # 4) Assert you get the proper status dict
    assert result["status"] == "success"
    assert result["sections_processed"] == len(fake_sections)
    assert result["doc_id"].startswith("doc_dummy")
