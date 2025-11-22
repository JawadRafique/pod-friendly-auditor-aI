# Pod-Friendly Auditor 🦾

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/pod-detection-auditor/blob/main/pod-auditor.ipynb)

An AI-powered accessibility detection system that runs on **Google Colab for FREE**! Train custom object detection models to identify accessibility features like pod signs, ramps, tactile paving, and elevators in public spaces - no local setup required.

## 🌟 Features

- **☁️ Cloud-Based**: Runs entirely on Google Colab - no local installation needed
- **⚡ GPU Training**: 10x faster training with free GPU acceleration
- **🌐 Public Access**: Share your app worldwide with a public URL
- **🖱️ Web-based GUI**: Easy-to-use interface accessible from any device
- **📝 Interactive Annotation**: Draw bounding boxes to label objects in images
- **🚀 One-Click Training**: Start GPU training with a simple button click
- **🔍 Real-time Testing**: Test your trained models instantly
- **📱 Mobile Friendly**: Works perfectly on phones and tablets

## 🎯 Detection Classes

The system is pre-configured to detect these accessibility features:

1. **Pod Sign** - Accessibility signage
2. **Ramp** - Wheelchair accessible ramps
3. **Tactile Paving** - Textured ground surfaces for visually impaired
4. **Elevator** - Accessible elevator entrances

## 🚀 Quick Start (5 Minutes to Live!)

### Prerequisites

- **Google Account** (free)
- **Internet Browser** (Chrome, Safari, Firefox, etc.)
- **That's it!** No downloads or installations needed

### Deploy to Google Colab

1. **Open Google Colab**: https://colab.research.google.com
2. **Create new notebook** 
3. **Get ngrok token**: https://dashboard.ngrok.com (free signup)
4. **Copy & run** the 5 code cells from `deploy-colab.py`
5. **Your Pod Auditor goes LIVE** with a public URL!

```
🌐 Your Pod Detection Auditor is LIVE at:
🔗 https://abc123.ngrok.io
```

**Share this URL with anyone worldwide!**

### First Use

1. **Open your browser** to your ngrok URL (e.g., https://abc123.ngrok.io)
2. **Upload images** containing accessibility features
3. **Annotate images** by drawing bounding boxes around objects
4. **Train the model** (15-30 minutes with GPU acceleration!)
5. **Test detection** on new images

## 📋 Detailed Usage Guide

### 1. Image Upload & Annotation

**Upload Images:**
- Click "Upload" in the navigation
- Drag & drop or select images (PNG, JPG, JPEG, GIF)
- Maximum 32MB per image (Colab has more memory than local)

**Annotate Objects:**
- Click "Annotate" next to uploaded images
- Select object class (pod_sign, ramp, etc.)
- Click and drag to create bounding boxes
- Save to training or validation dataset

**Annotation Tips:**
- Draw tight bounding boxes around objects
- Include various angles and lighting
- Aim for 20+ training images per class
- Use 5+ validation images per class

### 2. Model Training (GPU Accelerated!)

**Initial Training:**
- Go to "Train" tab
- Click "Start Initial Training"
- Uses YOLO11 Nano with GPU acceleration
- Takes 15-30 minutes (instead of 2-4 hours locally!)

**Fine-tuning:**
- Add more annotated images
- Click "Fine-Tune Model"
- Specify version name (v2, v3, etc.)
- Takes 10-15 minutes with GPU

**Training Benefits:**
- **⚡ GPU Speed**: 10x faster than local CPU training
- **🔄 Background Training**: Runs while you browse other tabs
- **📊 Real-time Progress**: Monitor training in Colab output
- **💾 Auto-save**: Models saved automatically in session

### 3. Testing & Inference

**Test Your Model:**
- Go to "Test" tab
- Upload a test image
- Click "Run Detection"
- View detected objects and confidence scores in seconds

**Understanding Results:**
- Confidence scores: 0.0 to 1.0 (higher = more confident)
- Bounding boxes show detected object locations
- Class labels identify object types
- GPU inference is much faster than CPU

## 🛠️ System Management (Google Colab)

### Session Management

```python
# Keep your Colab session active
import time
while True:
    print("⏰ Pod Auditor running...")
    time.sleep(60)
```

### Download Your Models

```python
# Download trained models before session ends
from google.colab import files
files.download('/content/pod-auditor/models/pod_model_v1/weights/best.pt')
```

### Upload Previous Models

```python
# Upload a previously trained model to continue training
from google.colab import files
uploaded = files.upload()
```

### Check GPU Status

```python
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory // 1e9:.0f} GB")
```

## 📁 Project Structure

```
pod-friendly-auditor/
├── deploy-colab.py            # 🚀 MAIN FILE: Copy this to Google Colab
├── COLAB-QUICKSTART.md        # Quick 5-minute setup guide
├── DEPLOYMENT.md              # Detailed deployment options
├── README.md                  # This file
└── (local files)              # Not needed for Colab deployment
    ├── datasets/              # Created automatically in Colab
    ├── models/                # Generated during training
    ├── web-interface/         # Flask templates (built-in to Colab script)
    ├── scripts/               # Training scripts (included in Colab)
    ├── Dockerfile            # For local Docker (not needed)
    ├── start.sh              # For local setup (not needed)
    └── stop.sh               # For local setup (not needed)
```

**🎯 For Google Colab deployment, you only need `deploy-colab.py`!**

## 🔧 Configuration

### Training Parameters

Edit `datasets/pod-data/data.yaml` to modify:
- Dataset paths
- Class names and count
- Training parameters

### Performance Tuning

For your Intel MacBook, the system is optimized with:
- **Small batch size** (4-8) for limited CPU
- **Reduced workers** (2) to prevent overload
- **YOLO11 Nano** (fastest model variant)
- **Reasonable epochs** (50 initial, 30 fine-tune)

### Adding New Classes

1. Edit `datasets/pod-data/data.yaml`
2. Update class names in `web-interface/app.py`
3. Restart the container

## 📊 Performance Expectations

### Google Colab (FREE)

- **🚀 Initial Training**: 15-30 minutes (with GPU) vs 2-4 hours (local CPU)
- **⚡ Fine-tuning**: 10-15 minutes (with GPU) vs 1-2 hours (local CPU)  
- **🔍 Inference**: 1-2 seconds per image (with GPU)
- **💾 Memory Usage**: Up to 12GB RAM (much more than local)
- **🔋 GPU**: Usually T4 GPU (15GB VRAM) - way better than Intel CPU!
- **💰 Cost**: 100% FREE

### Training Time Comparison

| Setup | Initial Training | Fine-tuning | Inference |
|-------|-----------------|-------------|-----------|
| **Google Colab (GPU)** | **15-30 min** | **10-15 min** | **1-2 sec** |
| Local Intel MacBook | 2-4 hours | 1-2 hours | 5-10 sec |

**🎯 Google Colab is 8-10x faster than local training!**

## 🐛 Troubleshooting

### Common Issues

**"No GPU available":**
```python
# Check GPU status
import torch
print(torch.cuda.is_available())

# If False, you can still use CPU (just slower)
# Or try: Runtime > Change runtime type > GPU
```

**"Session disconnected":**
- Colab disconnects after ~90 minutes of inactivity
- Run a cell occasionally to stay connected
- Download your models before session ends

**"ngrok tunnel error":**
- Get a free token from https://dashboard.ngrok.com
- Make sure you entered the token correctly
- Try rerunning the ngrok cell

**"Training fails":**
```python
# Check if you have training data
import os
print("Training images:", len(os.listdir('/content/pod-auditor/datasets/pod-data/train/images')))
print("Labels:", len(os.listdir('/content/pod-auditor/datasets/pod-data/train/labels')))
```

**"Out of memory":**
- Reduce batch size in training code
- Use smaller images
- Restart runtime: Runtime > Restart runtime

### Performance Issues

**Slow inference:**
- Make sure you're using the GPU runtime
- Check GPU availability with `torch.cuda.is_available()`

**Training not starting:**
- Ensure you have annotated images in training folder
- Check that data.yaml is correctly configured
- Verify YOLO model can load

## 📚 Advanced Usage

### Custom Model Configuration

Edit training scripts to modify:
- Epochs count
- Learning rate
- Batch size
- Image size

### Data Augmentation

The system includes automatic augmentation:
- Random rotations
- Color adjustments
- Mosaic augmentation
- Mixup augmentation

### Transfer Learning

Fine-tuning leverages transfer learning:
- Starts from pre-trained YOLO11 weights
- Adapts to your specific data
- Much faster than training from scratch

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

### Adding Features

1. **Web interface improvements**: Edit the Flask app in `deploy-colab.py`
2. **Training optimizations**: Modify training parameters for better results  
3. **New detection classes**: Add more accessibility features to detect

### Sharing Your Improvements

1. Fork this repository
2. Make your changes to `deploy-colab.py`
3. Test in Google Colab
4. Submit a pull request

## 📄 License

This project is open source. Use responsibly for accessibility improvements!

## 🙋‍♀️ Support

For issues:
1. Check this README and `COLAB-QUICKSTART.md`
2. Review Colab output for error messages
3. Check GPU availability with `torch.cuda.is_available()`
4. Try restarting your Colab runtime
5. Create a new Colab session if problems persist

## 🎯 Tips for Success

1. **Start with Google Colab**: Much faster and easier than local setup
2. **Use GPU when available**: Check Runtime > Change runtime type > GPU
3. **Quality over quantity**: Clear, well-lit images work best
4. **Diverse data**: Various angles, lighting, contexts
5. **Monitor session**: Keep Colab active to avoid disconnection
6. **Download models**: Save your work before session ends
7. **Share your URL**: Let others contribute training data

---

**Happy training! 🚀 Making public spaces more accessible, one detection at a time - now powered by free GPU acceleration!**