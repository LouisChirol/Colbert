#!/bin/bash

# Go to the root of the repository
cd "$(dirname "$0")/.."

# Server details
SERVER="ubuntu@145.239.71.174"
DEST_DIR="~/colbert"

# Create a temporary directory for the clean copy
TEMP_DIR=$(mktemp -d)

# Copy frontend (excluding node_modules and .next)
rsync -av --exclude 'node_modules' \
          --exclude '.next' \
          --exclude '.git' \
          frontend/ $TEMP_DIR/frontend/

# Verify public directory was copied
if [ ! -d "$TEMP_DIR/frontend/public" ]; then
    echo "Error: public directory not found in frontend!"
    exit 1
fi

# Copy backend (excluding __pycache__ and .venv)
rsync -av --exclude '__pycache__' \
          --exclude '.venv' \
          --exclude '.git' \
          backend/ $TEMP_DIR/backend/

# Create nginx directory and copy configuration
mkdir -p $TEMP_DIR/nginx
cp nginx/colbertchat.fr.conf $TEMP_DIR/nginx/

# Create scripts directory and copy deploy script
mkdir -p $TEMP_DIR/scripts
cp scripts/deploy.sh $TEMP_DIR/scripts/

# Copy other necessary files
cp docker-compose.yml $TEMP_DIR/

# Copy everything to the server
scp -i ~/.ssh/id_ed25519_colbert -r $TEMP_DIR/* $SERVER:$DEST_DIR/

# Verify public directory on server
ssh -i ~/.ssh/id_ed25519_colbert $SERVER "ls -la $DEST_DIR/frontend/public/"

# Make deploy script executable
ssh -i ~/.ssh/id_ed25519_colbert $SERVER "chmod +x $DEST_DIR/scripts/deploy.sh"

# Clean up
rm -rf $TEMP_DIR

echo "Files copied successfully! Now SSH into the server and run:"
echo "cd ~/colbert && ./scripts/deploy.sh" 