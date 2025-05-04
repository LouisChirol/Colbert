#!/bin/bash

# Create directory if it doesn't exist
mkdir -p ~/colbert
cd ~/colbert

# Clone or pull the repository
if [ -d ".git" ]; then
    echo "Pulling latest changes..."
    git pull
else
    echo "Cloning repository..."
    git clone <your-repository-url> .
fi

# Set environment variables
export MISTRAL_API_KEY=your-api-key

# Stop and remove existing containers
docker-compose down

# Remove old images to force rebuild
docker-compose rm -f
docker rmi $(docker images -q 'colbert_*') || true

# Build and start containers
docker-compose build --no-cache
docker-compose up -d

# Show container status
docker-compose ps

echo "Deployment complete! Your application is running at https://colbertchat.fr" 