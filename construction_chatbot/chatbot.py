from pathlib import Path
from typing import Dict, List
import logging
from datetime import datetime

from .document_processor import DocumentProcessor
from .retriever import DocumentRetriever

logger = logging.getLogger(__name__)

class ConstructionChatbot:
    def __init__(self):
        # Initialize our document processor and retriever
        self.processor = DocumentProcessor()
        self.retriever = DocumentRetriever()
        
        # Keep last 5 exchanges for context
        self.history: List[Dict] = []
    
    async def process_document(self, file_path: Path) -> Dict:
        """Process and store a construction document"""
        try:
            # Create an ID with date for better tracking
            doc_id = f"doc_{file_path.stem}_{datetime.now().strftime('%Y%m%d')}"
            
            # Process the document
            processed = self.processor.process_document(str(file_path), doc_id)
            
            # Store sections in vector DB
            await self.retriever.add_sections(doc_id, processed["sections"])
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "sections_processed": len(processed["sections"])
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise
    
    async def chat(self, message: str) -> Dict:
        """Handle a chat message with context"""
        try:
            # Get recent context if we have history
            context = self._get_context() if self.history else None
            
            # Query with context
            response = await self.retriever.query(message, context)
            
            # Update conversation history
            self.history.append({
                "question": message,
                "answer": response["answer"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep history manageable
            if len(self.history) > 5:
                self.history.pop(0)
            
            return response
            
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise
    
    def _get_context(self) -> str:
        """Format conversation context for the LLM"""
        context = ["Recent conversation:"]
        
        # Use last 2 exchanges for context window
        for entry in self.history[-2:]:
            context.append(f"Q: {entry['question']}")
            context.append(f"A: {entry['answer']}\n")
        
        return "\n".join(context)
    
    async def close(self):
        """Clean up resources"""
        await self.retriever.close()