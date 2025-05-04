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
├── frontend/        # Next.js web application
├── infra/          # Terraform configurations
└── scraper/        # Content ingestion scripts
```

## Technical Stack

- **Backend**: FastAPI, LangGraph/LangChain, Mistral AI
- **Frontend**: Next.js, TypeScript
- **Vector Store**: Chroma/Qdrant
- **Infrastructure**: Docker, Terraform, OVH KS-B
- **Data Processing**: Python, HTTPX, BeautifulSoup

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) license.

## Getting Started

Detailed setup instructions for each component can be found in their respective directories:

- [Backend Setup](backend/README.md)
- [Frontend Setup](frontend/README.md)
- [Infrastructure Setup](infra/README.md)
- [Scraper Setup](scraper/README.md)

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests. 
