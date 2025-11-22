#!/bin/bash

# Pod-Friendly Auditor Stop Script
# This script stops the pod detection system

echo "🛑 Stopping Pod-Friendly Auditor System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Stop and remove container
echo "🐳 Stopping Docker container..."
docker stop yolo-trainer > /dev/null 2>&1
docker rm yolo-trainer > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ System stopped successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Container may not have been running${NC}"
fi

echo ""
echo "📊 System Status:"
echo "• Web interface: Stopped"
echo "• Docker container: Removed"
echo "• Your data: Preserved in datasets/ and models/"
echo ""
echo -e "${GREEN}To restart the system, run: ./start.sh${NC}"