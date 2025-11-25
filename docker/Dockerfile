FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libopencv-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create necessary directories
RUN mkdir -p backend/database backend/face_encodings

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=backend/app.py
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "backend.app:create_app()"]