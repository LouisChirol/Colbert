#!/bin/bash

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

# Copy backend (excluding __pycache__ and .venv)
rsync -av --exclude '__pycache__' \
          --exclude '.venv' \
          --exclude '.git' \
          backend/ $TEMP_DIR/backend/

# Copy other necessary files
cp docker-compose.yml $TEMP_DIR/
cp setup-server.sh $TEMP_DIR/

# # Copy everything to the server
# scp  -i ~/.ssh/id_ed25519_colbert -r $TEMP_DIR/* $SERVER:$DEST_DIR/

# Clean up
rm -rf $TEMP_DIR

echo "Files copied successfully! Now SSH into the server and run:"
echo "cd ~/colbert && ./setup-server.sh" 