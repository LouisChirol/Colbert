copy-to-server.sh# Colbert Frontend

The web interface for Colbert, built with Next.js and TypeScript.

## Overview

The frontend provides a responsive chat interface that allows users to:
- Query French public administration information
- View responses with source citations
- Navigate to source documents
- Use the interface on both desktop and mobile devices

## Technical Stack

- Next.js 14
- TypeScript
- Tailwind CSS
- React Query
- Docker
- Prettier for code formatting

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

3. Start the development server:
```bash
npm run dev
```

## Features

- Responsive chat interface
- Source citation display
- Clickable source links
- Mobile-friendly design
- Dark/light mode support

## Development

- Run tests: `npm test`
- Build for production: `npm run build`
- Start development server: `npm run dev`
- Format code: `npm run format`
- Lint code: `npm run lint`
- Type check: `npm run type-check`

## Docker

Build and run the container:
```bash
docker build -t colbert-frontend .
docker run -p 3000:3000 colbert-frontend
```

## Environment Variables

Required environment variables:
- `NEXT_PUBLIC_API_URL`: URL of the backend service (e.g., http://localhost:8000)
- `NEXT_PUBLIC_APP_NAME`: Application name (defaults to "Colbert")
- `NEXT_PUBLIC_APP_DESCRIPTION`: Application description

Optional environment variables:
- `NEXT_PUBLIC_GA_ID`: Google Analytics ID (if enabled)
- `NEXT_PUBLIC_SENTRY_DSN`: Sentry DSN for error tracking (if enabled)

## Deployment

The frontend is designed to be served as a static build via Nginx. The build process generates optimized static files that can be served efficiently. 