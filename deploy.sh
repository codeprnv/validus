#!/bin/bash

# ==============================================================================
# Validus Enterprise KYC - Deployment Script for AWS EC2 (Ubuntu)
# ==============================================================================
# Run this script on a fresh Ubuntu EC2 instance to deploy the Validus system.
# Usage: sudo bash deploy.sh
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status

echo "🚀 Starting Validus Deployment..."

# 1. Update system and install dependencies
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl gnupg git

# 2. Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
else
    echo "✅ Docker is already installed."
fi

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# 3. Setup Project Directory
echo "📁 Setting up project directory..."
PROJECT_DIR="/opt/validus"

if [ -d "$PROJECT_DIR" ]; then
    echo "Directory $PROJECT_DIR exists. Pulling latest changes..."
    cd $PROJECT_DIR
    # Assuming the code is pushed to a Git repository.
    # Replace the URL below with your actual repository URL.
    # git pull origin main 
else
    echo "Creating project directory..."
    sudo mkdir -p $PROJECT_DIR
    sudo chown -R ubuntu:ubuntu $PROJECT_DIR
    cd $PROJECT_DIR
    
    # In a real scenario, you would clone your repo here:
    # git clone https://github.com/yourusername/validus.git .
    echo "⚠️  Note: You need to transfer/clone your project files into $PROJECT_DIR"
fi

# 4. Create .env file if it doesn't exist
echo "🔐 Configuring environment variables..."
if [ ! -f ".env" ]; then
    cat <<EOF > .env
API_KEY=aa6d7794571a5fcffae7da6946abcf7b303c9407a846ac90e236f4712042392c
ML_SERVICE_URL=http://ml-service:5000
API_GATEWAY_URL=http://api-gateway:8000/api/verify
EOF
    echo "Created default .env file."
fi

# 5. Build and Run the Docker Compose Stack
# We use -d to run in detached mode so the script can finish
echo "🏗️  Building and starting Docker containers..."
# This command expects the project files to be present in the directory
if [ -f "docker-compose.yml" ]; then
    sudo docker compose up -d --build
    echo "✅ Validus deployed successfully!"
    echo "🌍 Access the API at: http://<EC2-PUBLIC-IP>/docs"
    echo "💻 Access the UI at: http://<EC2-PUBLIC-IP>:8050"
    echo "📝 To view logs: docker compose logs -f"
else
    echo "❌ ERROR: docker-compose.yml not found in $PROJECT_DIR"
    echo "Please ensure project files are uploaded to this directory before running docker compose."
fi

echo "🎉 Deployment script finished."
