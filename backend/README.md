# Colbert Backend

The backend service for Colbert, a RAG-powered chatbot for French public administration information. Built with FastAPI and LangChain, it provides a robust API for handling chat interactions with AI-powered responses.

## Overview

The backend service provides:
- RESTful API endpoints for chat interactions
- RAG (Retrieval-Augmented Generation) powered responses
- Session management with Redis
- Vector search capabilities using ChromaDB
- Comprehensive logging system

## Technical Stack

- **Framework**: FastAPI
- **AI/ML**: 
  - LangChain/LangGraph
  - Mistral AI
  - ChromaDB (Vector Store)
- **Caching**: Redis
- **Logging**: Loguru
- **Python Version**: 3.11+

## Project Structure

```
backend/
├── main.py              # FastAPI application and endpoints
├── colbert_agent.py     # Core RAG agent implementation
├── colbert_prompt.py    # Prompt templates and management
├── search_tool.py       # Vector search implementation
├── redis_service.py     # Redis session management
├── chroma_db/          # Vector database storage
├── logs/               # Application logs
└── Dockerfile          # Container configuration
```

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `MISTRAL_API_KEY`: Your Mistral AI API key
- `REDIS_URL`: Redis connection URL
- `TAVILY_API_KEY`: Tavily search API key (for web search)
- `CHROMA_DB_PATH`: Path to ChromaDB storage

## Development

1. Start the development server:
```bash
uvicorn main:app --reload --port 8000
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### POST /chat
Main endpoint for chat interactions.

Request body:
```json
{
    "message": "string",
    "session_id": "string"
}
```

Response:
```json
{
    "answer": "string",
    "sources": [
        {
            "url": "string",
            "title": "string",
            "excerpt": "string"
        }
    ]
}
```

## Docker

Build and run the container:
```bash
docker build -t colbert-backend .
docker run -p 8000:8000 colbert-backend
```

## Logging

Logs are stored in the `logs/` directory with:
- Rotation: 10 MB per file
- Retention: 7 days
- Level: INFO

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) license. 