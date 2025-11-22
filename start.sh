#!/bin/bash

# Pod-Friendly Auditor Setup Script
# This script sets up and runs the complete pod detection system

set -e  # Exit on any error

echo "🏗️  Setting up Pod-Friendly Auditor System..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed and running
echo "🐳 Checking Docker..."
if ! docker --version > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Please install Docker Desktop for macOS first:"
    echo "https://docs.docker.com/desktop/install/mac-install/"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo -e "${GREEN}✅ Docker is ready${NC}"

# Get current directory
PROJECT_DIR=$(pwd)
echo "📁 Project directory: $PROJECT_DIR"

# Build Docker image
echo ""
echo "🔨 Building Docker image (this may take a few minutes)..."
docker build -t yolo-cpu .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Failed to build Docker image${NC}"
    exit 1
fi

# Stop existing container if running
echo ""
echo "🧹 Cleaning up any existing containers..."
docker stop yolo-trainer > /dev/null 2>&1 || true
docker rm yolo-trainer > /dev/null 2>&1 || true

# Run Docker container with volume mounts
echo ""
echo "🚀 Starting Docker container..."
docker run -d \
  --name yolo-trainer \
  -p 5000:5000 \
  -v "$PROJECT_DIR/datasets":/usr/src/app/datasets \
  -v "$PROJECT_DIR/models":/usr/src/app/runs \
  -v "$PROJECT_DIR/web-interface":/usr/src/app/web-interface \
  -v "$PROJECT_DIR/scripts":/usr/src/app/scripts \
  yolo-cpu

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start container${NC}"
    exit 1
fi

# Wait a moment for container to be ready
sleep 3

# Start web interface
echo ""
echo "🌐 Starting web interface..."
docker exec -d yolo-trainer python /usr/src/app/web-interface/app.py

# Wait for web server to start
echo "⏳ Waiting for web server to start..."
sleep 5

# Check if web server is responding
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Web interface is ready${NC}"
else
    echo -e "${YELLOW}⚠️  Web interface may take a moment to start${NC}"
fi

echo ""
echo "🎉 Pod-Friendly Auditor is ready!"
echo "=================================================="
echo ""
echo -e "${GREEN}🌐 Web Interface:${NC} http://localhost:5000"
echo ""
echo -e "${BLUE}📚 Quick Start Guide:${NC}"
echo "1. Open http://localhost:5000 in your browser"
echo "2. Upload images using the Upload tab"
echo "3. Annotate your images by drawing bounding boxes"
echo "4. Train your model using the Train tab"
echo "5. Test detection using the Test tab"
echo ""
echo -e "${BLUE}🐳 Docker Commands:${NC}"
echo "• View logs: docker logs yolo-trainer"
echo "• Stop system: docker stop yolo-trainer"
echo "• Restart: docker start yolo-trainer"
echo "• Shell access: docker exec -it yolo-trainer bash"
echo ""
echo -e "${YELLOW}💡 Performance Note:${NC}"
echo "Training will be slow on Intel CPU (2-4 hours for initial training)"
echo "Start with 10-20 annotated images per class for best results"
echo ""
echo -e "${GREEN}Happy training! 🚀${NC}"