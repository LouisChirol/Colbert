# Colbert

A lightweight RAG-powered chatbot for querying French public administration procedures, laws, and official guidelines.


## Work in progress
See PR agent_refactor for the work in progress about the RAG feature from the data.gouv dump of the service-public website.

## Overview

Colbert provides a simple web/mobile interface to access information from Service-Public.fr and other official French government sources. The system uses RAG (Retrieval-Augmented Generation) to provide accurate, sourced responses in French.

## Features

- Real-time access to French public administration information
- Strictly sourced responses from official channels
- French language interface and responses
- No user data retention (GDPR-compliant)
- Daily automatic content updates
- Responsive web/mobile interface

## Project Structure

```
colbert/
├── backend/         # FastAPI service and RAG pipeline
├── database/        # Data processing and vector store
├── frontend/        # Next.js web application
├── nginx/          # Nginx configuration
├── scripts/        # Utility scripts
└── docker-compose.yml  # Docker compose configuration
```

## Technical Stack

- **Backend**: 
  - FastAPI
  - LangChain/LangGraph
  - Mistral AI
  - Redis for session management
- **Frontend**: 
  - Next.js 14
  - TypeScript
  - Tailwind CSS
- **Database**: 
  - ChromaDB (Vector Store)
  - PostgreSQL
- **Infrastructure**: 
  - Docker & Docker Compose
  - Nginx

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) license.
