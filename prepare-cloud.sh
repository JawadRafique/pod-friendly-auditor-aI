#!/bin/bash

# Quick deployment script for cloud hosting
echo "🌐 Preparing Pod Detection Auditor for Cloud Deployment"

# Create .gitignore for cloud deployment
cat > .gitignore << EOF
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/

# Local data (don't upload to cloud)
datasets/pod-data/train/images/*
datasets/pod-data/val/images/*
datasets/pod-data/uploaded/*
models/*
runs/*
!datasets/pod-data/train/images/.gitkeep
!datasets/pod-data/val/images/.gitkeep
!datasets/pod-data/uploaded/.gitkeep
!models/.gitkeep

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Docker (keep for local development)
# Dockerfile
EOF

# Create placeholder files to maintain directory structure
touch datasets/pod-data/train/images/.gitkeep
touch datasets/pod-data/train/labels/.gitkeep
touch datasets/pod-data/val/images/.gitkeep
touch datasets/pod-data/val/labels/.gitkeep
touch datasets/pod-data/uploaded/.gitkeep
touch models/.gitkeep

echo "✅ Cloud deployment files created!"
echo ""
echo "🚀 Next steps for hosting online:"
echo "1. Push to GitHub: git add . && git commit -m 'Pod Auditor' && git push"
echo "2. Deploy on Railway.app: https://railway.app"
echo "3. Or use GitHub Codespaces for development"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions"