import pytest
from construction_chatbot.chatbot import ConstructionChatbot

@pytest.mark.asyncio
async def test_process_document_fallback(monkeypatch, tmp_path):
    # Create a dummy PDF
    dummy = tmp_path / "dummy.pdf"
    dummy.write_bytes(b"%PDF-1.4\n%%EOF")

    fake_sections = [{"title": "HEAD", "content": "BODY", "page": 1}]

    # Mock the document processor to return fake sections
    monkeypatch.setattr(
        "construction_chatbot.document_processor.DocumentProcessor.process_document",
        lambda self, path, doc_id: {"sections": fake_sections}
    )

    # async mock for add_sections
    async def fake_add_sections(self, doc_id, sections):
        return None

    monkeypatch.setattr(
        "construction_chatbot.retriever.DocumentRetriever.add_sections",
        fake_add_sections
    )

    # Now test the actual method
    bot = ConstructionChatbot()
    result = await bot.process_document(dummy)

    assert result["status"] == "success"
    assert result["sections_processed"] == 1

