import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from loguru import logger
from colbert_agent import ColbertAgent

# Load environment variables
load_dotenv()

# Delete the old log file if it exists
if os.path.exists("logs/colbert_backend.log"):
    os.remove("logs/colbert_backend.log")

# Configure logger
logger.add("logs/colbert_backend.log", rotation="10 MB", retention="7 days", level="INFO")

app = FastAPI(
    title="Colbert Backend",
    description="RAG-powered chatbot for French public administration information",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str


class Source(BaseModel):
    url: str
    title: str
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


@app.get("/")
async def root():
    return {"message": "Welcome to Colbert API"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info(f"Processing chat request for session: {request.session_id}")
        colbert_agent = ColbertAgent()
        # Generate response using chat history for context
        answer = colbert_agent.ask_colbert(request.message, request.session_id)

        return ChatResponse(
            answer=answer,
            sources=[],  # You can add sources if you implement RAG later
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
