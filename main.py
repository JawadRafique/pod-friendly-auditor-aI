#!/usr/bin/env python3
"""
Cloud-optimized startup script for pod detection web interface
This version is designed for cloud platforms like Railway, Render, Heroku
"""

import os
import sys
from web_interface.app import app

if __name__ == '__main__':
    # Get port from environment variable (required for cloud platforms)
    port = int(os.environ.get('PORT', 5000))
    
    # Get host from environment (0.0.0.0 for cloud deployment)
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🌐 Starting Pod Detection Auditor on {host}:{port}")
    print("🚀 Cloud deployment mode")
    
    # Run Flask app
    app.run(host=host, port=port, debug=False)