#!/usr/bin/env python3
"""
Fine-tuning script for pod detection model
Continues training from previous best model with new data
"""

import os
import sys
from ultralytics import YOLO

def retrain_model(previous_model_path=None, version="v2"):
    """Fine-tune the model with new data"""
    
    if previous_model_path is None:
        previous_model_path = '/usr/src/app/runs/pod_model_v1/weights/best.pt'
    
    print(f"🔄 Starting fine-tuning for Pod Detection Model {version}...")
    print(f"📂 Loading previous model from: {previous_model_path}")
    
    # Check if previous model exists
    if not os.path.exists(previous_model_path):
        print(f"❌ Previous model not found at {previous_model_path}")
        print("🔄 Starting from base YOLO11n model instead...")
        model = YOLO('yolo11n.pt')
    else:
        # Load your pre-trained model
        model = YOLO(previous_model_path)
        print("✅ Previous model loaded successfully!")
    
    # Fine-tuning parameters
    results = model.train(
        data='/usr/src/app/datasets/pod-data/data.yaml',
        epochs=30,  # Fewer epochs for fine-tuning
        imgsz=640,
        batch=4,
        workers=2,
        device='cpu',
        project='/usr/src/app/runs',
        name=f'pod_model_{version}',
        save_period=5,
        patience=15,
        verbose=True,
        resume=False  # Start fresh fine-tuning
    )
    
    print("✅ Fine-tuning completed!")
    print(f"📊 Results: {results}")
    print(f"💾 Updated model saved to: /usr/src/app/runs/pod_model_{version}/weights/best.pt")
    
    return results

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        version = sys.argv[1]
    else:
        version = "v2"
    
    if len(sys.argv) > 2:
        previous_model = sys.argv[2]
    else:
        previous_model = None
    
    retrain_model(previous_model, version)