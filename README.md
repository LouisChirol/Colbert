# Colbert

A lightweight RAG-powered chatbot for querying French public administration procedures, laws, and official guidelines.

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
├── database/        # Database migrations and schemas
├── frontend/        # Next.js web application
├── nginx/          # Nginx configuration for production
├── scripts/        # Utility scripts and tools
└── docker-compose.yml  # Docker compose configuration
```

## Technical Stack

- **Backend**: FastAPI, LangGraph/LangChain, Mistral AI
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Database**: PostgreSQL
- **Vector Store**: Chroma/Qdrant
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Data Processing**: Python, HTTPX, BeautifulSoup

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) license.

## Getting Started

Detailed setup instructions for each component can be found in their respective directories:

- [Backend Setup](backend/README.md)
- [Frontend Setup](frontend/README.md)
- [Database Setup](database/README.md)

For local development, you can use Docker Compose to start all services:
```bash
docker-compose up
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests. 
