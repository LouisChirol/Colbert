from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from mistral_agent import ask_mistral
import uuid

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Colbert Backend",
    description="RAG-powered chatbot for French public administration information",
    version="0.1.0"
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
        answer = ask_mistral(request.message)
        return ChatResponse(
            answer=answer,
            sources=[]  # You can add sources if you implement RAG later
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 