from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from pathlib import Path
import logging
from datetime import datetime

from app.chatbot import ConstructionChatbot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Construction Document Assistant",
    description="Chat with your construction documents using AI"
)

# CORS - allowing all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot = ConstructionChatbot()

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a construction document"""
    start_time = datetime.now()
    
    try:
        # Save uploaded file safely
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_path = Path(tmp_file.name)
        
        try:
            # Process the document
            result = await chatbot.process_document(temp_path)
            
            # Log processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Processed {file.filename} in {processing_time:.2f}s - "
                f"{result['sections_processed']} sections"
            )
            
            return result
            
        finally:
            # Always clean up temp file
            temp_path.unlink(missing_ok=True)
            
    except Exception as e:
        logger.error(f"Failed to process {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(message: str):
    """Chat with the construction document assistant"""
    try:
        start_time = datetime.now()
        response = await chatbot.chat(message)
        
        # Log response time
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Generated response in {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    try:
        await chatbot.close()
        logger.info("Shutdown successful")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )