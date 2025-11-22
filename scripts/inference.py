#!/usr/bin/env python3
"""
Inference script for testing the trained pod detection model
"""

import os
import sys
from ultralytics import YOLO
from PIL import Image

def run_inference(model_path, image_path, save_results=True):
    """Run inference on an image using the trained model"""
    
    print(f"🔍 Running inference with model: {model_path}")
    print(f"📸 Processing image: {image_path}")
    
    # Load the trained model
    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        return None
    
    model = YOLO(model_path)
    
    # Run inference
    results = model(image_path)
    
    # Process results
    for r in results:
        # Get detection info
        boxes = r.boxes
        if boxes is not None:
            print(f"✅ Found {len(boxes)} objects:")
            for i, box in enumerate(boxes):
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls]
                print(f"  - Object {i+1}: {class_name} (confidence: {conf:.2f})")
        else:
            print("🔍 No objects detected")
        
        # Save results if requested
        if save_results:
            output_path = "/usr/src/app/inference_results/"
            os.makedirs(output_path, exist_ok=True)
            annotated = r.plot()
            result_image = Image.fromarray(annotated)
            result_file = os.path.join(output_path, f"result_{os.path.basename(image_path)}")
            result_image.save(result_file)
            print(f"💾 Results saved to: {result_file}")
    
    return results

def test_latest_model(image_path=None):
    """Test the latest trained model"""
    
    # Find the latest model
    runs_dir = "/usr/src/app/runs"
    model_path = None
    
    # Look for the latest version
    for version in ["v3", "v2", "v1"]:
        potential_path = f"{runs_dir}/pod_model_{version}/weights/best.pt"
        if os.path.exists(potential_path):
            model_path = potential_path
            break
    
    if model_path is None:
        print("❌ No trained model found!")
        return None
    
    print(f"🎯 Using model: {model_path}")
    
    # Use a test image if none provided
    if image_path is None:
        # Look for test images in the dataset
        test_images = []
        val_dir = "/usr/src/app/datasets/pod-data/val/images"
        if os.path.exists(val_dir):
            for file in os.listdir(val_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_images.append(os.path.join(val_dir, file))
        
        if test_images:
            image_path = test_images[0]
        else:
            print("❌ No test images found!")
            return None
    
    return run_inference(model_path, image_path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Model path provided
        model_path = sys.argv[1]
        image_path = sys.argv[2] if len(sys.argv) > 2 else None
        if image_path:
            run_inference(model_path, image_path)
        else:
            print("Usage: python inference.py <model_path> <image_path>")
    else:
        # Test latest model
        test_latest_model()