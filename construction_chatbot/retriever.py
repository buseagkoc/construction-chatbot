import asyncio
import chromadb
import openai
import redis.asyncio as redis
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class DocumentRetriever:
    def __init__(self):
        # Initialize vector store for document sections
        self.vector_store = chromadb.Client()
        self.collection = self.vector_store.create_collection("construction_docs")
        
        # Redis for caching frequent queries
        self.redis = redis.from_url(settings.REDIS_URL)
        
        # Rate limiting - I hit OpenAI's rate limits at >5 concurrent
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_CALLS)
        
        # Batch processing queue
        self.batch_queue = []
        self.last_process_time = datetime.now()
    
    async def add_sections(self, doc_id: str, sections: List[Dict]):
        # Add unique identifier to prevent overwrites
        unique_doc_id = f"{doc_id}_{uuid.uuid4().hex[:8]}"
        
        self.batch_queue.append({
            "doc_id": unique_doc_id,
            "sections": sections,
            "timestamp": datetime.now()
        })
        
        # Process batch if full or if it's been waiting too long
        if (len(self.batch_queue) >= settings.BATCH_SIZE or 
            (datetime.now() - self.last_process_time).seconds > 60):
            await self._process_batch()
    
    async def _process_batch(self):
        if not self.batch_queue:
            return
            
        try:
            docs = []
            metadata = []
            ids = []
            
            for item in self.batch_queue:
                for idx, section in enumerate(item["sections"]):
                    docs.append(section["content"])
                    metadata.append({
                        "doc_id": item["doc_id"],
                        "title": section["title"],
                        "page": section["page"],
                        "processed_at": datetime.now().isoformat()
                    })
                    ids.append(f"{item['doc_id']}_section_{idx}")
            
            # Add to vector store
            self.collection.add(
                documents=docs,
                metadatas=metadata,
                ids=ids
            )
            
            self.last_process_time = datetime.now()
            self.batch_queue = []
            
        except Exception as e:
            logger.error(f"Failed to process batch: {e}")
            raise
    
    async def query(self, question: str, context: Optional[str] = None) -> Dict:
        cache_key = f"query:{question}"
        
        try:
            # Check cache first
            if cached := await self.redis.get(cache_key):
                return json.loads(cached)
            
            # Search vector store
            results = self.collection.query(
                query_texts=[question],
                n_results=3  # Found that 3 gives good context without noise
            )
            
            if not results["documents"] or not results["documents"][0]:
                return {
                    "answer": "I couldn't find anything relevant in the docs. Could you try rephrasing?",
                    "sources": []
                }
            
            # Rate limit API calls
            async with self.semaphore:
                response = await self._generate_response(question, results, context)
            
            # Cache for 5 minutes
            await self.redis.set(
                cache_key,
                json.dumps(response),
                ex=300
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    async def _generate_response(
        self,
        question: str,
        results: Dict,
        context: Optional[str] = None
    ) -> Dict:
        try:
            prompt = self._format_prompt(question, results, context)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4-turbo-preview",  # Most capable for technical docs
                messages=[
                    {"role": "system", "content": "You are a construction document assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "answer": response.choices[0].message.content,
                "sources": [
                    {
                        "title": meta["title"],
                        "page": meta["page"],
                        "doc_id": meta["doc_id"]
                    }
                    for meta in results["metadatas"][0]
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise
    
    def _format_prompt(self, question: str, results: Dict, context: Optional[str]) -> str:
        parts = []
        
        if context:
            parts.append(context)
        
        if results["documents"] and results["documents"][0]:
            parts.append("Relevant sections:")
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                parts.append(f"\nSection: {meta['title']} (Page {meta['page']})")
                parts.append(f"Content: {doc}")
        else:
            parts.append("No relevant sections found.")
        
        parts.append(f"\nQuestion: {question}")
        return "\n".join(parts)
    
    async def close(self):
        try:
            # Clean up any remaining docs
            if self.batch_queue:
                await self._process_batch()
            await self.redis.close()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise
