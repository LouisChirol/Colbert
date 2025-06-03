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

Required environment variables:
- `MISTRAL_API_KEY`: Your Mistral AI API key
- `REDIS_URL`: Redis connection URL
- `CHROMA_DB_PATH`: Path to ChromaDB storage

## Development

1. Start the development server:
```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

### POST /chat
Main endpoint for chat interactions.

## Docker

Build and run the container:
```bash
docker build -t colbert-backend .
docker run -p 8000:8000 colbert-backend
```

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) license. 