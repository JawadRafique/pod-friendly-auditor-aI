#!/usr/bin/env python3
"""
Initial training script for pod detection model
Optimized for CPU training on Intel MacBook
"""

import os
import sys
from ultralytics import YOLO

def train_initial_model():
    """Train the initial YOLO11 model for pod detection"""
    
    print("🚀 Starting initial training for Pod Detection Model...")
    print("⚠️  This is optimized for CPU training - it will take some time on Intel MacBook")
    
    # Load YOLO11 nano model (fastest for CPU)
    model = YOLO('yolo11n.pt')
    
    # Training parameters optimized for CPU
    results = model.train(
        data='/usr/src/app/datasets/pod-data/data.yaml',
        epochs=50,  # Start with fewer epochs for testing
        imgsz=640,  # Standard image size
        batch=4,    # Small batch for CPU
        workers=2,  # Limited workers
        device='cpu',  # Force CPU usage
        project='/usr/src/app/runs',
        name='pod_model_v1',
        save_period=10,  # Save checkpoint every 10 epochs
        patience=20,  # Early stopping patience
        verbose=True
    )
    
    print("✅ Training completed!")
    print(f"📊 Results: {results}")
    print(f"💾 Model saved to: /usr/src/app/runs/pod_model_v1/weights/best.pt")
    
    return results

if __name__ == "__main__":
    train_initial_model()