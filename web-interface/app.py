#!/usr/bin/env python3
"""
Flask web application for pod detection training interface
Provides GUI for image upload, annotation, and model training
"""

import os
import json
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuration
UPLOAD_FOLDER = '/usr/src/app/datasets/pod-data/uploaded'
TRAIN_IMAGES = '/usr/src/app/datasets/pod-data/train/images'
TRAIN_LABELS = '/usr/src/app/datasets/pod-data/train/labels'
VAL_IMAGES = '/usr/src/app/datasets/pod-data/val/images'
VAL_LABELS = '/usr/src/app/datasets/pod-data/val/labels'
INFERENCE_RESULTS = '/usr/src/app/inference_results'

# Create directories if they don't exist
for directory in [UPLOAD_FOLDER, TRAIN_IMAGES, TRAIN_LABELS, VAL_IMAGES, VAL_LABELS, INFERENCE_RESULTS]:
    os.makedirs(directory, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
CLASS_NAMES = ['pod_sign', 'ramp', 'tactile_paving', 'elevator']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', classes=CLASS_NAMES)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file uploads"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{unique_id}_{secure_filename(file.filename)}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Get image dimensions for annotation
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
            except Exception as e:
                return jsonify({'error': f'Invalid image file: {str(e)}'}), 400
            
            return jsonify({
                'success': True,
                'filename': filename,
                'width': width,
                'height': height
            })
    
    return render_template('upload.html')

@app.route('/annotate/<filename>')
def annotate(filename):
    """Annotation interface for uploaded images"""
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    
    # Get image dimensions
    with Image.open(file_path) as img:
        width, height = img.size
    
    return render_template('annotate.html', 
                         filename=filename, 
                         width=width, 
                         height=height, 
                         classes=CLASS_NAMES)

@app.route('/save_annotations', methods=['POST'])
def save_annotations():
    """Save annotations and move image to training dataset"""
    data = request.json
    filename = data.get('filename')
    annotations = data.get('annotations', [])
    dataset_type = data.get('dataset_type', 'train')  # train or val
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    # Source file path
    source_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(source_path):
        return jsonify({'error': 'Source file not found'}), 404
    
    # Determine destination paths
    if dataset_type == 'val':
        img_dest = VAL_IMAGES
        label_dest = VAL_LABELS
    else:
        img_dest = TRAIN_IMAGES
        label_dest = TRAIN_LABELS
    
    # Move image to destination
    base_name = os.path.splitext(filename)[0]
    img_dest_path = os.path.join(img_dest, filename)
    label_dest_path = os.path.join(label_dest, f"{base_name}.txt")
    
    # Copy image
    import shutil
    shutil.move(source_path, img_dest_path)
    
    # Save annotations in YOLO format
    with Image.open(img_dest_path) as img:
        img_width, img_height = img.size
    
    with open(label_dest_path, 'w') as f:
        for ann in annotations:
            class_id = ann['class_id']
            x_center = ann['x_center'] / img_width
            y_center = ann['y_center'] / img_height
            width_norm = ann['width'] / img_width
            height_norm = ann['height'] / img_height
            
            f.write(f"{class_id} {x_center} {y_center} {width_norm} {height_norm}\n")
    
    return jsonify({
        'success': True,
        'message': f'Image and annotations saved to {dataset_type} dataset'
    })

@app.route('/train', methods=['GET', 'POST'])
def train():
    """Training interface"""
    if request.method == 'POST':
        training_type = request.form.get('training_type', 'initial')
        
        if training_type == 'initial':
            # Start initial training
            try:
                process = subprocess.Popen(
                    ['python', '/usr/src/app/scripts/train_initial.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                return jsonify({'success': True, 'message': 'Initial training started', 'type': 'initial'})
            except Exception as e:
                return jsonify({'error': f'Failed to start training: {str(e)}'}), 500
        
        elif training_type == 'retrain':
            version = request.form.get('version', 'v2')
            previous_model = request.form.get('previous_model', '')
            
            try:
                cmd = ['python', '/usr/src/app/scripts/retrain.py', version]
                if previous_model:
                    cmd.append(previous_model)
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                return jsonify({'success': True, 'message': f'Fine-tuning started for version {version}', 'type': 'retrain'})
            except Exception as e:
                return jsonify({'error': f'Failed to start fine-tuning: {str(e)}'}), 500
    
    # GET request - show training interface
    return render_template('train.html')

@app.route('/inference', methods=['GET', 'POST'])
def inference():
    """Inference interface"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, f"test_{filename}")
            file.save(temp_path)
            
            try:
                # Run inference
                result = subprocess.run(
                    ['python', '/usr/src/app/scripts/inference.py', 'latest', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Clean up temp file
                os.remove(temp_path)
                
                if result.returncode == 0:
                    return jsonify({
                        'success': True,
                        'output': result.stdout,
                        'message': 'Inference completed successfully'
                    })
                else:
                    return jsonify({
                        'error': f'Inference failed: {result.stderr}'
                    }), 500
                    
            except subprocess.TimeoutExpired:
                return jsonify({'error': 'Inference timeout'}), 500
            except Exception as e:
                return jsonify({'error': f'Inference error: {str(e)}'}), 500
    
    return render_template('inference.html')

@app.route('/status')
def status():
    """System status and statistics"""
    stats = {
        'train_images': len([f for f in os.listdir(TRAIN_IMAGES) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]),
        'val_images': len([f for f in os.listdir(VAL_IMAGES) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]),
        'uploaded_images': len([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]),
        'models_trained': 0  # Will be calculated below
    }
    
    # Count trained models
    runs_dir = '/usr/src/app/runs'
    if os.path.exists(runs_dir):
        model_dirs = [d for d in os.listdir(runs_dir) if d.startswith('pod_model_')]
        stats['models_trained'] = len(model_dirs)
        stats['model_versions'] = model_dirs
    else:
        stats['model_versions'] = []
    
    return render_template('status.html', stats=stats)

@app.route('/uploaded/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/results/<filename>')
def result_file(filename):
    """Serve inference result files"""
    return send_from_directory(INFERENCE_RESULTS, filename)

if __name__ == '__main__':
    # Get port from environment variable for cloud deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)