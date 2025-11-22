"""
🚀 COMPLETE Google Colab Deployment for Pod Detection Auditor
============================================================

INSTRUCTIONS:
1. Open Google Colab: https://colab.research.google.com
2. Create a new notebook
3. Copy each CELL below into separate cells in Colab
4. Run cells in order
5. Get your public URL and share!

This creates a complete, functional Pod Detection Auditor with GPU support!
"""

print("""
🎯 COPY THE FOLLOWING CELLS INTO GOOGLE COLAB:
==============================================
""")

print("""
# =================== CELL 1: SETUP ===================
print("🚀 Setting up Pod Detection Auditor in Google Colab...")
print("🔥 With GPU acceleration and public web interface!")
print("=" * 60)

# Check GPU availability
import torch
if torch.cuda.is_available():
    print(f"✅ GPU Available: {torch.cuda.get_device_name(0)}")
    print(f"🔋 GPU Memory: {torch.cuda.get_device_properties(0).total_memory // 1e9:.0f} GB")
else:
    print("⚠️  GPU not available - using CPU (slower training)")

# Install all dependencies
print("📦 Installing dependencies...")
!pip install -q ultralytics flask pillow opencv-python-headless pyngrok werkzeug

# Setup ngrok for public access
from pyngrok import ngrok
import getpass

print("\\n🔐 Setup ngrok for public access:")
print("1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken")
print("2. Sign up (free) and copy your authtoken")
authtoken = getpass.getpass("Paste your ngrok authtoken: ")
ngrok.set_auth_token(authtoken)

print("✅ Setup complete!")

# =================== CELL 2: CREATE PROJECT ===================
import os
import shutil
from pathlib import Path
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import threading
import time

print("📁 Creating project structure...")

# Create directories
dirs = [
    'pod-auditor/datasets/pod-data/train/images',
    'pod-auditor/datasets/pod-data/train/labels',
    'pod-auditor/datasets/pod-data/val/images', 
    'pod-auditor/datasets/pod-data/val/labels',
    'pod-auditor/datasets/pod-data/uploaded',
    'pod-auditor/models',
    'pod-auditor/templates',
    'pod-auditor/static'
]

for d in dirs:
    Path(d).mkdir(parents=True, exist_ok=True)

# Create dataset config
yaml_config = '''path: /content/pod-auditor/datasets/pod-data
train: train/images
val: val/images
nc: 4
names: ['pod_sign', 'ramp', 'tactile_paving', 'elevator']
'''

with open('pod-auditor/datasets/pod-data/data.yaml', 'w') as f:
    f.write(yaml_config)

print("✅ Project structure created!")

# =================== CELL 3: WEB APPLICATION ===================
print("🌐 Creating web application...")

# Main Flask app
app_code = '''
import os
import json
import subprocess
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
import torch

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

# Configuration
UPLOAD_FOLDER = '/content/pod-auditor/datasets/pod-data/uploaded'
TRAIN_IMAGES = '/content/pod-auditor/datasets/pod-data/train/images'
TRAIN_LABELS = '/content/pod-auditor/datasets/pod-data/train/labels'
VAL_IMAGES = '/content/pod-auditor/datasets/pod-data/val/images'
VAL_LABELS = '/content/pod-auditor/datasets/pod-data/val/labels'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
CLASS_NAMES = ['pod_sign', 'ramp', 'tactile_paving', 'elevator']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    gpu_info = f"GPU: {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else "CPU Only"
    return render_template('index.html', classes=CLASS_NAMES, gpu_info=gpu_info)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file'}), 400
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        with Image.open(file_path) as img:
            width, height = img.size
        
        return jsonify({
            'success': True,
            'filename': filename,
            'width': width, 
            'height': height
        })
    return render_template('upload.html')

@app.route('/annotate/<filename>')
def annotate(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    with Image.open(file_path) as img:
        width, height = img.size
    return render_template('annotate.html', filename=filename, width=width, height=height, classes=CLASS_NAMES)

@app.route('/save_annotations', methods=['POST'])
def save_annotations():
    data = request.json
    filename = data['filename']
    annotations = data.get('annotations', [])
    dataset_type = data.get('dataset_type', 'train')
    
    source = os.path.join(UPLOAD_FOLDER, filename)
    if dataset_type == 'val':
        img_dest, label_dest = VAL_IMAGES, VAL_LABELS
    else:
        img_dest, label_dest = TRAIN_IMAGES, TRAIN_LABELS
    
    base_name = os.path.splitext(filename)[0]
    img_path = os.path.join(img_dest, filename)
    label_path = os.path.join(label_dest, f"{base_name}.txt")
    
    shutil.move(source, img_path)
    
    with Image.open(img_path) as img:
        img_w, img_h = img.size
    
    with open(label_path, 'w') as f:
        for ann in annotations:
            x_center = ann['x_center'] / img_w
            y_center = ann['y_center'] / img_h
            width = ann['width'] / img_w  
            height = ann['height'] / img_h
            f.write(f"{ann['class_id']} {x_center} {y_center} {width} {height}\\n")
    
    return jsonify({'success': True})

@app.route('/train', methods=['GET', 'POST'])
def train():
    if request.method == 'POST':
        training_type = request.form.get('training_type')
        if training_type == 'initial':
            def run_train():
                from ultralytics import YOLO
                model = YOLO('yolo11n.pt')
                model.train(
                    data='/content/pod-auditor/datasets/pod-data/data.yaml',
                    epochs=50,
                    batch=16 if torch.cuda.is_available() else 8,
                    device='cuda' if torch.cuda.is_available() else 'cpu',
                    project='/content/pod-auditor/models',
                    name='pod_model_v1'
                )
            threading.Thread(target=run_train).start()
            return jsonify({'success': True, 'message': 'Training started!'})
    return render_template('train.html')

@app.route('/inference', methods=['GET', 'POST'])
def inference():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        temp_path = f"/tmp/{filename}"
        file.save(temp_path)
        
        try:
            from ultralytics import YOLO
            model_path = '/content/pod-auditor/models/pod_model_v1/weights/best.pt'
            if os.path.exists(model_path):
                model = YOLO(model_path)
                results = model(temp_path)
                detections = []
                for r in results:
                    if r.boxes:
                        for box in r.boxes:
                            cls = int(box.cls[0])
                            conf = float(box.conf[0])
                            detections.append({
                                'class': model.names[cls],
                                'confidence': f"{conf:.2f}"
                            })
                os.remove(temp_path)
                return jsonify({'success': True, 'detections': detections})
            else:
                return jsonify({'error': 'No trained model found'})
        except Exception as e:
            return jsonify({'error': str(e)})
    return render_template('inference.html')

@app.route('/status')
def status():
    stats = {
        'train_images': len([f for f in os.listdir(TRAIN_IMAGES) if f.endswith(('.jpg', '.png'))]),
        'val_images': len([f for f in os.listdir(VAL_IMAGES) if f.endswith(('.jpg', '.png'))]),
        'uploaded': len([f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(('.jpg', '.png'))]),
        'gpu': torch.cuda.is_available()
    }
    return render_template('status.html', stats=stats)

@app.route('/uploaded/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
'''

with open('pod-auditor/app.py', 'w') as f:
    f.write(app_code)

print("✅ Web application created!")

# =================== CELL 4: HTML TEMPLATES ===================
print("📄 Creating HTML templates...")

# Main template
index_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Pod Detection Auditor - Colab</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 3rem 0; }
        .card-hover:hover { transform: translateY(-5px); transition: 0.3s; }
        .gpu-badge { position: fixed; top: 20px; right: 20px; z-index: 1000; }
    </style>
</head>
<body>
    <div class="gpu-badge">
        <span class="badge bg-success fs-6">{{ gpu_info }}</span>
    </div>
    
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-eye"></i> Pod Auditor</a>
            <span class="navbar-text text-warning">Colab Edition</span>
        </div>
    </nav>

    <div class="hero">
        <div class="container text-center">
            <h1 class="display-4"><i class="fas fa-universal-access"></i> Pod Detection Auditor</h1>
            <p class="lead">AI-powered accessibility detection on Google Colab</p>
        </div>
    </div>

    <div class="container mt-5">
        <div class="row g-4">
            <div class="col-md-3">
                <div class="card h-100 shadow card-hover">
                    <div class="card-body text-center">
                        <i class="fas fa-upload fa-2x text-primary mb-3"></i>
                        <h5>Upload</h5>
                        <a href="/upload" class="btn btn-primary">Upload Images</a>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card h-100 shadow card-hover">
                    <div class="card-body text-center">
                        <i class="fas fa-brain fa-2x text-success mb-3"></i>
                        <h5>Train</h5>
                        <a href="/train" class="btn btn-success">Train Model</a>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card h-100 shadow card-hover">
                    <div class="card-body text-center">
                        <i class="fas fa-search fa-2x text-info mb-3"></i>
                        <h5>Test</h5>
                        <a href="/inference" class="btn btn-info">Test Model</a>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card h-100 shadow card-hover">
                    <div class="card-body text-center">
                        <i class="fas fa-chart-bar fa-2x text-warning mb-3"></i>
                        <h5>Status</h5>
                        <a href="/status" class="btn btn-warning">View Status</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

# Create all templates with minimal but functional versions
templates = {
    'index.html': index_html,
    'upload.html': '''<!DOCTYPE html><html><head><title>Upload</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"></head><body><div class="container mt-5"><h2>Upload Images</h2><div id="upload-area" style="border: 2px dashed #ccc; padding: 50px; text-align: center;"><input type="file" id="file-input" multiple accept="image/*" style="display:none;"><button onclick="document.getElementById('file-input').click()" class="btn btn-primary">Choose Files</button></div><div id="uploaded-files"></div></div><script>document.getElementById('file-input').addEventListener('change', function(e) { Array.from(e.target.files).forEach(file => { const formData = new FormData(); formData.append('file', file); fetch('/upload', { method: 'POST', body: formData }).then(r => r.json()).then(data => { if(data.success) { const div = document.createElement('div'); div.innerHTML = `<div class="card mt-2"><div class="card-body"><strong>${data.filename}</strong> <a href="/annotate/${data.filename}" class="btn btn-sm btn-primary">Annotate</a></div></div>`; document.getElementById('uploaded-files').appendChild(div); } }); }); });</script></body></html>''',
    'annotate.html': '''<!DOCTYPE html><html><head><title>Annotate</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"><style>.annotation-container{position:relative;display:inline-block}.annotation-image{max-width:100%}.bounding-box{position:absolute;border:2px solid #007bff;background:rgba(0,123,255,0.1);cursor:move}</style></head><body><div class="container mt-3"><h3>Annotate: {{filename}}</h3><div class="row"><div class="col-3"><h5>Classes:</h5>{% for i, cls in enumerate(classes) %}<button class="btn btn-sm btn-outline-primary mb-1 class-btn" data-class-id="{{i}}" data-class="{{cls}}">{{cls}}</button><br>{% endfor %}<br><button id="save-train" class="btn btn-success">Save to Training</button><button id="save-val" class="btn btn-info">Save to Validation</button></div><div class="col-9"><div class="annotation-container" id="container"><img src="/uploaded/{{filename}}" class="annotation-image" id="image"></div></div></div></div><script>let currentClass=0,annotations=[];document.querySelectorAll('.class-btn').forEach((btn,i)=>{btn.onclick=()=>{document.querySelectorAll('.class-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');currentClass=i;}});document.querySelector('.class-btn').click();document.getElementById('container').addEventListener('mousedown',e=>{if(e.target.id!=='image')return;const rect=e.target.getBoundingClientRect(),startX=e.clientX-rect.left,startY=e.clientY-rect.top;const box=document.createElement('div');box.className='bounding-box';box.style.left=startX+'px';box.style.top=startY+'px';document.getElementById('container').appendChild(box);function onMouseMove(e){const width=Math.abs(e.clientX-rect.left-startX),height=Math.abs(e.clientY-rect.top-startY);box.style.width=width+'px';box.style.height=height+'px';}function onMouseUp(){document.removeEventListener('mousemove',onMouseMove);document.removeEventListener('mouseup',onMouseUp);const width=parseInt(box.style.width),height=parseInt(box.style.height);if(width>10&&height>10){annotations.push({class_id:currentClass,x_center:parseInt(box.style.left)+width/2,y_center:parseInt(box.style.top)+height/2,width,height});}else{box.remove();}}document.addEventListener('mousemove',onMouseMove);document.addEventListener('mouseup',onMouseUp);});document.getElementById('save-train').onclick=()=>save('train');document.getElementById('save-val').onclick=()=>save('val');function save(type){fetch('/save_annotations',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({filename:'{{filename}}',annotations,dataset_type:type})}).then(r=>r.json()).then(data=>{if(data.success){alert('Saved!');window.location='/upload';}});}</script></body></html>''',
    'train.html': '''<!DOCTYPE html><html><head><title>Train</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"></head><body><div class="container mt-5"><h2>Train Model</h2><div class="card"><div class="card-body"><h5>Start Training</h5><p>This will train a YOLO11 model on your annotated data</p><button id="start-train" class="btn btn-success">Start Initial Training</button><div id="status" class="mt-3"></div></div></div></div><script>document.getElementById('start-train').onclick=()=>{const formData=new FormData();formData.append('training_type','initial');fetch('/train',{method:'POST',body:formData}).then(r=>r.json()).then(data=>{document.getElementById('status').innerHTML=data.success?'<div class="alert alert-success">Training started! Check Colab output for progress.</div>':'<div class="alert alert-danger">Error: '+data.error+'</div>';});};</script></body></html>''',
    'inference.html': '''<!DOCTYPE html><html><head><title>Test</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"></head><body><div class="container mt-5"><h2>Test Model</h2><div class="card"><div class="card-body"><input type="file" id="test-file" accept="image/*" class="form-control mb-3"><button id="test-btn" class="btn btn-primary">Run Detection</button><div id="results" class="mt-3"></div></div></div></div><script>document.getElementById('test-btn').onclick=()=>{const file=document.getElementById('test-file').files[0];if(!file)return;const formData=new FormData();formData.append('file',file);fetch('/inference',{method:'POST',body:formData}).then(r=>r.json()).then(data=>{const div=document.getElementById('results');if(data.success){div.innerHTML='<div class="alert alert-success"><h5>Detections:</h5>'+data.detections.map(d=>`<p>${d.class} (confidence: ${d.confidence})</p>`).join('')+'</div>';}else{div.innerHTML='<div class="alert alert-danger">Error: '+data.error+'</div>';}});};</script></body></html>''',
    'status.html': '''<!DOCTYPE html><html><head><title>Status</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"></head><body><div class="container mt-5"><h2>System Status</h2><div class="row"><div class="col-md-3"><div class="card bg-primary text-white"><div class="card-body text-center"><h3>{{stats.train_images}}</h3><p>Training Images</p></div></div></div><div class="col-md-3"><div class="card bg-info text-white"><div class="card-body text-center"><h3>{{stats.val_images}}</h3><p>Validation Images</p></div></div></div><div class="col-md-3"><div class="card bg-warning text-white"><div class="card-body text-center"><h3>{{stats.uploaded}}</h3><p>Pending Annotation</p></div></div></div><div class="col-md-3"><div class="card bg-success text-white"><div class="card-body text-center"><h3>{{"Yes" if stats.gpu else "No"}}</h3><p>GPU Available</p></div></div></div></div></div></body></html>'''
}

for name, content in templates.items():
    with open(f'pod-auditor/templates/{name}', 'w') as f:
        f.write(content)

print("✅ All templates created!")

# =================== CELL 5: LAUNCH APPLICATION ===================
print("🚀 Starting Pod Detection Auditor...")

# Start ngrok tunnel
public_url = ngrok.connect(5000)
print(f"\\n🌐 Your Pod Detection Auditor is LIVE at:")
print(f"🔗 {public_url}")
print("\\n" + "="*60)

# Start Flask app
import sys
import subprocess
sys.path.append('/content/pod-auditor')

def run_app():
    os.chdir('/content/pod-auditor')
    subprocess.run(['python', 'app.py'])

app_thread = threading.Thread(target=run_app)
app_thread.daemon = True
app_thread.start()

# Wait for app to start
time.sleep(5)

print("\\n🎉 SUCCESS! Your Pod Detection Auditor is running!")
print("=" * 60)
print(f"🌐 Public URL: {public_url}")
print("📱 Access this URL from any device")
print("🚀 Features available:")
print("   • Upload and annotate images") 
print("   • GPU-accelerated training")
print("   • Real-time object detection")
print("   • Web interface for everything")
print("\\n💡 This URL stays active while your Colab session runs!")
print("📋 Bookmark it and share with others!")

# Keep the session alive
try:
    while True:
        time.sleep(60)
        print(f"⏰ Pod Auditor running... {time.strftime('%H:%M:%S')}")
except KeyboardInterrupt:
    print("\\n🛑 Stopping Pod Detection Auditor...")
    ngrok.disconnect(public_url)
'''

print("\\n🎯 INSTRUCTIONS:")
print("1. Open https://colab.research.google.com")
print("2. Create new notebook")  
print("3. Copy each CELL above into separate cells")
print("4. Run cells in order")
print("5. Get your ngrok token from: https://dashboard.ngrok.com")
print("6. Your Pod Auditor will be live with a public URL!")

print("\\n✨ Your Google Colab deployment is ready!")