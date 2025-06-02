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
```

## Technical Stack

- **Backend**: FastAPI, LangGraph/LangChain, Mistral AI
- **Frontend**: Next.js, TypeScript
- **Vector Store**: Chroma
- **Infrastructure**: Docker, Terraform, OVH KS-B

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) license.
