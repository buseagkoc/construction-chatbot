import pytest
from construction_chatbot.chatbot import ConstructionChatbot

@pytest.mark.asyncio
async def test_chat_returns_string(monkeypatch):
    async def fake_query(self, question, context=None):
        return {"answer": "mocked", "sources": []}

    monkeypatch.setattr("construction_chatbot.retriever.DocumentRetriever.query", fake_query)
    
    bot = ConstructionChatbot()
    result = await bot.chat("Mock me please")
    assert isinstance(result["answer"], str)
