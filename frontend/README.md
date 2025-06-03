# Colbert Frontend

The web interface for Colbert, built with Next.js and TypeScript. Provides a responsive chat interface for querying French public administration information.

## Overview

The frontend provides a responsive chat interface that allows users to:
- Query French public administration information
- View responses with source citations
- Navigate to source documents
- Use the interface on both desktop and mobile devices

## Technical Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query
- **Code Quality**: 
  - Prettier for formatting
  - ESLint for linting
- **Containerization**: Docker

## Project Structure

```
frontend/
├── src/              # Source code
│   ├── app/         # Next.js app directory
│   ├── components/  # React components
│   └── lib/         # Utility functions
├── public/          # Static assets
├── Dockerfile       # Container configuration
└── package.json     # Dependencies and scripts
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

Required environment variables:
- `NEXT_PUBLIC_API_URL`: Backend service URL (e.g., http://localhost:8000)
- `NEXT_PUBLIC_APP_NAME`: Application name (defaults to "Colbert")
- `NEXT_PUBLIC_APP_DESCRIPTION`: Application description

Optional environment variables:
- `NEXT_PUBLIC_GA_ID`: Google Analytics ID (if enabled)
- `NEXT_PUBLIC_SENTRY_DSN`: Sentry DSN for error tracking (if enabled)

## Development

1. Start the development server:
```bash
npm run dev
```

2. Available commands:
- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run start`: Start production server
- `npm run lint`: Run ESLint
- `npm run format`: Format code with Prettier
- `npm run type-check`: Run TypeScript type checking

## Features

- Responsive chat interface
- Source citation display
- Clickable source links
- Mobile-friendly design
- Dark/light mode support
- Real-time chat updates
- Error handling and retry logic

## Docker

Build and run the container:
```bash
docker build -t colbert-frontend .
docker run -p 3000:3000 colbert-frontend
```

## Deployment

The frontend is designed to be served as a static build via Nginx. The build process generates optimized static files that can be served efficiently.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) license. 