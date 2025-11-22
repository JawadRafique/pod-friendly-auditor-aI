# Use lightweight Python 3.11 for better compatibility
FROM python:3.11-slim

# Set environment variables for better performance on CPU
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system libraries needed for OpenCV and other dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# Install Python packages
# We install CPU-only versions for better performance on Intel MacBook
RUN pip install --no-cache-dir \
    ultralytics \
    flask \
    pillow \
    opencv-python-headless \
    numpy \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy application files
COPY web-interface/ ./web-interface/
COPY scripts/ ./scripts/

# Expose port for web interface
EXPOSE 5000

# Create volume mount points
VOLUME ["/usr/src/app/datasets", "/usr/src/app/runs"]

# Keep the container running so we can send commands to it
CMD ["tail", "-f", "/dev/null"]